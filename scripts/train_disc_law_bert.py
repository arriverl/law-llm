#!/usr/bin/env python3
"""
基于DISC-LawLLM架构的BERT模型训练脚本
参考: https://github.com/FudanDISC/DISC-LawLLM
"""
import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.disc_law_bert import DISCLawBERT, GBALegalDataProcessor

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="训练基于DISC-LawLLM架构的BERT模型")
    parser.add_argument("--data_dir", type=str, default="data/disc_law_data",
                        help="数据目录路径")
    parser.add_argument("--model_name", type=str, default="bert-base-chinese",
                        help="预训练模型名称")
    parser.add_argument("--output_dir", type=str, default="./models/disc_law_bert",
                        help="模型输出目录")
    parser.add_argument("--epochs", type=int, default=5,
                        help="训练轮数")
    parser.add_argument("--batch_size", type=int, default=16,
                        help="批次大小")
    parser.add_argument("--learning_rate", type=float, default=2e-5,
                        help="学习率")
    parser.add_argument("--max_length", type=int, default=512,
                        help="最大序列长度")
    parser.add_argument("--warmup_steps", type=int, default=500,
                        help="预热步数")
    parser.add_argument("--test_size", type=float, default=0.2,
                        help="测试集比例")
    
    args = parser.parse_args()
    
    logger.info("🌏 基于DISC-LawLLM架构的BERT模型训练")
    logger.info("=" * 60)
    logger.info(f"数据目录: {args.data_dir}")
    logger.info(f"模型名称: {args.model_name}")
    logger.info(f"输出目录: {args.output_dir}")
    logger.info(f"训练轮数: {args.epochs}")
    logger.info(f"批次大小: {args.batch_size}")
    logger.info(f"学习率: {args.learning_rate}")
    
    try:
        # 1. 初始化模型配置
        logger.info("\n1. 初始化DISC-LawLLM BERT模型配置...")
        config = {
            'model_name': args.model_name,
            'num_labels': 10,  # 10个法律类别
            'max_length': args.max_length,
            'epochs': args.epochs,
            'batch_size': args.batch_size,
            'learning_rate': args.learning_rate,
            'warmup_steps': args.warmup_steps,
            'output_dir': args.output_dir
        }
        
        # 2. 初始化模型
        logger.info("\n2. 初始化DISC-LawLLM BERT模型...")
        model = DISCLawBERT(config)
        
        # 3. 加载数据
        logger.info("\n3. 加载粤港澳大湾区法律数据...")
        data_processor = GBALegalDataProcessor(args.data_dir)
        texts, labels = data_processor.load_data()
        
        if not texts:
            logger.error("未找到训练数据，请先运行数据收集脚本")
            return
        
        logger.info(f"加载了 {len(texts)} 条训练数据")
        
        # 4. 准备数据集
        logger.info("\n4. 准备数据集...")
        dataset_dict = model.prepare_dataset(texts, labels, test_size=args.test_size)
        
        # 5. 训练模型
        logger.info("\n5. 开始训练DISC-LawLLM BERT模型...")
        start_time = datetime.now()
        metrics = model.train(dataset_dict)
        end_time = datetime.now()
        
        training_time = (end_time - start_time).total_seconds()
        logger.info(f"训练完成，耗时: {training_time:.2f} 秒")
        
        # 6. 保存模型
        logger.info("\n6. 保存模型...")
        model.save_model(args.output_dir)
        
        # 7. 显示训练结果
        logger.info("\n🎉 DISC-LawLLM BERT模型训练完成!")
        logger.info(f"📊 训练指标:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        logger.info(f"📁 模型保存在: {args.output_dir}")
        logger.info(f"⏱️ 训练时间: {training_time:.2f} 秒")
        
        # 8. 创建模型使用说明
        usage_file = os.path.join(args.output_dir, "README.md")
        with open(usage_file, 'w', encoding='utf-8') as f:
            f.write(f"""# DISC-LawLLM BERT模型

## 模型信息
- 模型类型: 基于DISC-LawLLM架构的法律BERT模型
- 预训练模型: {args.model_name}
- 训练数据: 粤港澳大湾区法律数据
- 类别数量: 10个法律类别
- 训练时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 训练指标
""")
            for metric, value in metrics.items():
                f.write(f"- {metric}: {value:.4f}\n")
            
            f.write(f"""
## 使用方法

```python
from backend.app.services.disc_law_bert import DISCLawBERT

# 加载模型
model = DISCLawBERT.load_model('{args.output_dir}')

# 预测文本类别
texts = ["根据合同法规定...", "刑法修正案..."]
results = model.predict(texts)

for result in results:
    print(f"文本: {result['text']}")
    print(f"预测类别: {result['predicted_label']}")
    print(f"置信度: {result['confidence']:.4f}")
```

## 法律类别
1. 民事
2. 刑事
3. 行政
4. 商事
5. 劳动
6. 知识产权
7. 环境
8. 国际
9. 金融
10. 其他
""")
        
        logger.info(f"📖 使用说明已保存到: {usage_file}")
        
    except Exception as e:
        logger.error(f"训练失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())






