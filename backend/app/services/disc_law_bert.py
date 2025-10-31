#!/usr/bin/env python3
"""
基于DISC-LawLLM架构的法律BERT模型训练系统
参考: https://github.com/FudanDISC/DISC-LawLLM
"""
import os
import sys
import json
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Transformers相关
from transformers import (
    BertTokenizer, 
    BertForSequenceClassification,
    BertConfig,
    TrainingArguments, 
    Trainer,
    EarlyStoppingCallback,
    DataCollatorWithPadding
)
from datasets import Dataset, DatasetDict
import evaluate

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DISCLawBERT:
    """基于DISC-LawLLM架构的法律BERT模型"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.trainer = None
        self.metrics = {}
        
        # 初始化模型和分词器
        self._initialize_model()
        
    def _initialize_model(self):
        """初始化模型和分词器"""
        model_name = self.config.get('model_name', 'bert-base-chinese')
        num_labels = self.config.get('num_labels', 10)
        
        logger.info(f"初始化模型: {model_name}")
        
        # 加载分词器
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        
        # 加载模型配置
        model_config = BertConfig.from_pretrained(
            model_name,
            num_labels=num_labels,
            hidden_dropout_prob=0.1,
            attention_probs_dropout_prob=0.1
        )
        
        # 加载模型
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            config=model_config
        )
        
        logger.info(f"模型初始化完成，标签数量: {num_labels}")
    
    def prepare_dataset(self, texts: List[str], labels: List[int], 
                       test_size: float = 0.2, random_state: int = 42) -> DatasetDict:
        """准备数据集"""
        logger.info("准备数据集...")
        
        # 分割数据集
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=test_size, random_state=random_state, stratify=labels
        )
        
        # 创建数据集
        train_dataset = Dataset.from_dict({
            "text": train_texts,
            "labels": train_labels
        })
        
        val_dataset = Dataset.from_dict({
            "text": val_texts,
            "labels": val_labels
        })
        
        # 分词处理
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"], 
                padding=True, 
                truncation=True, 
                max_length=self.config.get('max_length', 512)
            )
        
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        val_dataset = val_dataset.map(tokenize_function, batched=True)
        
        # 创建数据集字典
        dataset_dict = DatasetDict({
            "train": train_dataset,
            "validation": val_dataset
        })
        
        logger.info(f"数据集准备完成 - 训练集: {len(train_dataset)}, 验证集: {len(val_dataset)}")
        return dataset_dict
    
    def compute_metrics(self, eval_pred):
        """计算评估指标"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')
        precision = precision_score(labels, predictions, average='weighted')
        recall = recall_score(labels, predictions, average='weighted')
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train(self, dataset_dict: DatasetDict, output_dir: str = None):
        """训练模型"""
        if output_dir is None:
            output_dir = self.config.get('output_dir', './models/disc_law_bert')
        
        logger.info("开始训练DISC-LawLLM BERT模型...")
        
        # 训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config.get('epochs', 5),
            per_device_train_batch_size=self.config.get('batch_size', 16),
            per_device_eval_batch_size=self.config.get('batch_size', 16),
            learning_rate=self.config.get('learning_rate', 2e-5),
            warmup_steps=self.config.get('warmup_steps', 500),
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=100,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            save_total_limit=3,
            evaluation_strategy="epoch",
            report_to=None,  # 禁用wandb
        )
        
        # 数据整理器
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # 创建训练器
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset_dict["train"],
            eval_dataset=dataset_dict["validation"],
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # 开始训练
        logger.info("开始训练...")
        train_result = self.trainer.train()
        
        # 保存模型
        self.trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        # 保存训练结果
        self.metrics = train_result.metrics
        logger.info(f"训练完成，最终指标: {self.metrics}")
        
        return self.metrics
    
    def evaluate(self, test_texts: List[str], test_labels: List[int]) -> Dict[str, float]:
        """评估模型"""
        logger.info("评估模型性能...")
        
        # 准备测试数据
        test_dataset = Dataset.from_dict({
            "text": test_texts,
            "labels": test_labels
        })
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"], 
                padding=True, 
                truncation=True, 
                max_length=self.config.get('max_length', 512)
            )
        
        test_dataset = test_dataset.map(tokenize_function, batched=True)
        
        # 评估
        eval_result = self.trainer.evaluate(test_dataset)
        
        logger.info(f"评估结果: {eval_result}")
        return eval_result
    
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """预测文本类别"""
        logger.info(f"预测 {len(texts)} 个文本的类别...")
        
        # 准备数据
        dataset = Dataset.from_dict({"text": texts})
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"], 
                padding=True, 
                truncation=True, 
                max_length=self.config.get('max_length', 512)
            )
        
        dataset = dataset.map(tokenize_function, batched=True)
        
        # 预测
        predictions = self.trainer.predict(dataset)
        predicted_labels = np.argmax(predictions.predictions, axis=1)
        predicted_probs = torch.softmax(torch.tensor(predictions.predictions), dim=1).numpy()
        
        # 返回结果
        results = []
        for i, (text, label, probs) in enumerate(zip(texts, predicted_labels, predicted_probs)):
            results.append({
                "text": text,
                "predicted_label": int(label),
                "confidence": float(np.max(probs)),
                "probabilities": probs.tolist()
            })
        
        return results
    
    def save_model(self, output_dir: str):
        """保存模型"""
        logger.info(f"保存模型到: {output_dir}")
        
        # 保存模型和分词器
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # 保存配置
        config_file = os.path.join(output_dir, "disc_law_bert_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        
        # 保存训练指标
        if self.metrics:
            metrics_file = os.path.join(output_dir, "training_metrics.json")
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        
        logger.info("模型保存完成")
    
    @classmethod
    def load_model(cls, model_dir: str):
        """加载预训练模型"""
        logger.info(f"加载模型: {model_dir}")
        
        # 加载配置
        config_file = os.path.join(model_dir, "disc_law_bert_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 创建实例
        instance = cls(config)
        
        # 加载模型
        instance.model = BertForSequenceClassification.from_pretrained(model_dir)
        instance.tokenizer = BertTokenizer.from_pretrained(model_dir)
        
        logger.info("模型加载完成")
        return instance

class GBALegalDataProcessor:
    """粤港澳大湾区法律数据处理器"""
    
    def __init__(self, data_dir: str = "data/gba_legal_data"):
        self.data_dir = data_dir
        self.legal_categories = {
            "民事": ["合同", "协议", "履行", "违约", "赔偿", "债务", "财产", "婚姻", "继承"],
            "刑事": ["犯罪", "刑罚", "刑事", "起诉", "判决", "量刑", "盗窃", "抢劫", "故意伤害"],
            "行政": ["行政", "政府", "处罚", "复议", "许可", "审批", "执法", "监管"],
            "商事": ["公司", "股东", "董事", "企业", "投资", "贸易", "股权", "并购"],
            "劳动": ["劳动", "员工", "工资", "社保", "工伤", "解雇", "加班", "休假"],
            "知识产权": ["专利", "商标", "版权", "知识产权", "侵权", "发明", "创作"],
            "环境": ["环境", "污染", "保护", "生态", "排放", "治理", "可持续发展"],
            "国际": ["国际", "仲裁", "贸易", "投资", "合作", "条约", "外交"],
            "金融": ["银行", "证券", "保险", "金融", "投资", "理财", "贷款"],
            "其他": ["其他", "综合", "一般"]
        }
    
    def load_data(self) -> Tuple[List[str], List[int]]:
        """加载粤港澳大湾区法律数据"""
        logger.info("加载粤港澳大湾区法律数据...")
        
        texts = []
        labels = []
        
        # 从JSON文件加载数据
        json_file = os.path.join(self.data_dir, "gba_legal_data.json")
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                text = item.get('text', '')
                category = item.get('category', '其他')
                
                if text and category:
                    texts.append(text)
                    labels.append(self._get_category_id(category))
        
        # 如果没有数据，创建示例数据
        if not texts:
            logger.warning("未找到数据文件，创建示例数据...")
            texts, labels = self._create_sample_data()
        
        logger.info(f"加载了 {len(texts)} 条法律数据")
        return texts, labels
    
    def _get_category_id(self, category: str) -> int:
        """获取类别ID"""
        for i, (cat_name, keywords) in enumerate(self.legal_categories.items()):
            if category == cat_name or any(keyword in category for keyword in keywords):
                return i
        return len(self.legal_categories) - 1  # 默认为"其他"
    
    def _create_sample_data(self) -> Tuple[List[str], List[int]]:
        """创建示例数据"""
        sample_texts = [
            "根据《中华人民共和国合同法》规定，合同是平等主体的自然人、法人、其他组织之间设立、变更、终止民事权利义务关系的协议。",
            "最高人民法院发布了关于审理民间借贷案件适用法律若干问题的规定。",
            "知识产权包括著作权、专利权和商标权等。",
            "劳动合同的解除应当遵循法定程序。",
            "刑法修正案（十一）对多项罪名进行了调整。",
            "公司法对公司的设立、组织机构、股份发行等作出了详细规定。",
            "消费者权益保护法旨在保护消费者的合法权益。",
            "行政诉讼是公民、法人或者其他组织认为行政机关的具体行政行为侵犯其合法权益，向人民法院提起诉讼的活动。",
            "婚姻家庭编是民法典的重要组成部分，调整婚姻家庭关系。",
            "环境保护法是国家为保护和改善环境，防治污染和其他公害，保障公众健康，促进经济社会可持续发展而制定的法律。"
        ]
        
        sample_labels = [0, 0, 6, 4, 1, 3, 0, 2, 0, 7]  # 对应的类别ID
        
        return sample_texts, sample_labels

def main():
    """主函数"""
    logger.info("🌏 粤港澳大湾区DISC-LawLLM BERT模型训练")
    logger.info("=" * 60)
    
    # 配置参数
    config = {
        'model_name': 'bert-base-chinese',
        'num_labels': 10,
        'max_length': 512,
        'epochs': 5,
        'batch_size': 16,
        'learning_rate': 2e-5,
        'warmup_steps': 500,
        'output_dir': './models/disc_law_bert'
    }
    
    try:
        # 1. 初始化模型
        logger.info("1. 初始化DISC-LawLLM BERT模型...")
        model = DISCLawBERT(config)
        
        # 2. 加载数据
        logger.info("2. 加载粤港澳大湾区法律数据...")
        data_processor = GBALegalDataProcessor()
        texts, labels = data_processor.load_data()
        
        # 3. 准备数据集
        logger.info("3. 准备数据集...")
        dataset_dict = model.prepare_dataset(texts, labels)
        
        # 4. 训练模型
        logger.info("4. 开始训练模型...")
        metrics = model.train(dataset_dict)
        
        # 5. 保存模型
        logger.info("5. 保存模型...")
        model.save_model(config['output_dir'])
        
        logger.info("🎉 DISC-LawLLM BERT模型训练完成!")
        logger.info(f"📊 训练指标: {metrics}")
        logger.info(f"📁 模型保存在: {config['output_dir']}")
        
    except Exception as e:
        logger.error(f"训练失败: {e}")
        raise

if __name__ == "__main__":
    main()






