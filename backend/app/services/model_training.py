"""
BERT法律模型训练服务
"""
import os
import json
import torch
import pandas as pd
from typing import List, Dict, Any
from transformers import (
    BertTokenizer, 
    BertForSequenceClassification,
    TrainingArguments, 
    Trainer,
    AutoTokenizer,
    AutoModelForSequenceClassification
)
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np

class LegalDataset(Dataset):
    """法律文本数据集"""
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class LegalBERTTrainer:
    """法律BERT模型训练器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.trainer = None
        
    def setup_model(self):
        """设置模型和分词器"""
        model_name = self.config.get('model_name', 'bert-base-chinese')
        
        # 加载分词器
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        
        # 加载模型
        num_labels = self.config.get('num_labels', 10)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )
        
        print(f"✅ 模型设置完成: {model_name}")
        print(f"📊 分类标签数量: {num_labels}")
    
    def prepare_data(self, data_path: str):
        """准备训练数据"""
        print("📚 准备训练数据...")
        
        # 读取数据
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        elif data_path.endswith('.json'):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            raise ValueError("支持的数据格式: CSV, JSON")
        
        # 数据预处理
        texts = df['text'].tolist()
        labels = df['label'].tolist()
        
        # 分割数据集
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # 创建数据集
        train_dataset = LegalDataset(
            train_texts, train_labels, self.tokenizer, self.config.get('max_length', 512)
        )
        val_dataset = LegalDataset(
            val_texts, val_labels, self.tokenizer, self.config.get('max_length', 512)
        )
        
        print(f"📈 训练集大小: {len(train_dataset)}")
        print(f"📈 验证集大小: {len(val_dataset)}")
        
        return train_dataset, val_dataset
    
    def compute_metrics(self, eval_pred):
        """计算评估指标"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='weighted'
        )
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train(self, train_dataset, val_dataset):
        """开始训练"""
        print("🚀 开始训练BERT模型...")
        
        # 训练参数
        training_args = TrainingArguments(
            output_dir=self.config.get('output_dir', './models/trained'),
            num_train_epochs=self.config.get('epochs', 3),
            per_device_train_batch_size=self.config.get('batch_size', 16),
            per_device_eval_batch_size=self.config.get('batch_size', 16),
            learning_rate=self.config.get('learning_rate', 2e-5),
            warmup_steps=self.config.get('warmup_steps', 500),
            logging_dir='./logs',
            logging_steps=100,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
        )
        
        # 创建训练器
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics,
        )
        
        # 开始训练
        self.trainer.train()
        
        # 保存模型
        self.trainer.save_model()
        self.tokenizer.save_pretrained(self.config.get('output_dir', './models/trained'))
        
        print("✅ 训练完成！模型已保存")
        
        # 评估模型
        eval_results = self.trainer.evaluate()
        print("📊 最终评估结果:")
        for key, value in eval_results.items():
            print(f"  {key}: {value:.4f}")
    
    def predict(self, text: str):
        """使用训练好的模型进行预测"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("模型未加载，请先训练或加载模型")
        
        # 编码输入
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.config.get('max_length', 512),
            return_tensors='pt'
        )
        
        # 预测
        with torch.no_grad():
            outputs = self.model(**encoding)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = torch.max(predictions).item()
        
        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'probabilities': predictions.numpy().tolist()
        }

def create_sample_data():
    """创建示例训练数据"""
    sample_data = [
        {"text": "合同双方应当按照约定履行义务", "label": 0},  # 合同法
        {"text": "用人单位应当为劳动者缴纳社会保险", "label": 1},  # 劳动法
        {"text": "侵犯他人知识产权应当承担法律责任", "label": 2},  # 知识产权法
        {"text": "交通事故责任认定需要根据具体情况", "label": 3},  # 侵权法
        {"text": "婚姻关系存续期间财产归属问题", "label": 4},  # 婚姻法
        {"text": "公司设立需要满足法定条件", "label": 5},  # 公司法
        {"text": "刑事案件审理程序应当合法", "label": 6},  # 刑法
        {"text": "行政诉讼中举证责任分配", "label": 7},  # 行政法
        {"text": "国际商事仲裁裁决执行", "label": 8},  # 国际法
        {"text": "环境保护法律责任追究", "label": 9},  # 环境法
    ]
    
    # 扩展数据
    extended_data = []
    for item in sample_data:
        # 为每个类别创建多个变体
        for i in range(10):
            extended_data.append({
                "text": f"{item['text']} - 变体{i+1}",
                "label": item['label']
            })
    
    return extended_data

def main():
    """主训练函数"""
    # 训练配置
    config = {
        'model_name': 'bert-base-chinese',
        'num_labels': 10,
        'max_length': 512,
        'epochs': 3,
        'batch_size': 16,
        'learning_rate': 2e-5,
        'warmup_steps': 500,
        'output_dir': './models/legal-bert-trained'
    }
    
    # 创建训练器
    trainer = LegalBERTTrainer(config)
    
    # 设置模型
    trainer.setup_model()
    
    # 创建示例数据
    print("📝 创建示例训练数据...")
    sample_data = create_sample_data()
    
    # 保存数据到文件
    data_path = './data/training/legal_data.json'
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    # 准备数据
    train_dataset, val_dataset = trainer.prepare_data(data_path)
    
    # 开始训练
    trainer.train(train_dataset, val_dataset)
    
    # 测试预测
    print("\n🧪 测试模型预测:")
    test_texts = [
        "合同违约应当承担违约责任",
        "员工加班费计算标准",
        "商标侵权案件处理"
    ]
    
    for text in test_texts:
        result = trainer.predict(text)
        print(f"文本: {text}")
        print(f"预测类别: {result['predicted_class']}")
        print(f"置信度: {result['confidence']:.4f}")
        print("-" * 50)

if __name__ == "__main__":
    main()
