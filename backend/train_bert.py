#!/usr/bin/env python3
"""
BERT法律模型训练启动脚本
"""
import os
import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from app.services.data_collector import LegalDataCollector
from app.services.model_training import LegalBERTTrainer

def main():
    parser = argparse.ArgumentParser(description='训练法律BERT模型')
    parser.add_argument('--data_path', type=str, default='./data/training/legal_training_data.json',
                       help='训练数据路径')
    parser.add_argument('--output_dir', type=str, default='./models/legal-bert-trained',
                       help='模型输出目录')
    parser.add_argument('--epochs', type=int, default=3,
                       help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='批次大小')
    parser.add_argument('--learning_rate', type=float, default=2e-5,
                       help='学习率')
    parser.add_argument('--max_length', type=int, default=512,
                       help='最大文本长度')
    parser.add_argument('--collect_data', action='store_true',
                       help='是否先收集数据')
    
    args = parser.parse_args()
    
    print("🤖 法律BERT模型训练")
    print("=" * 50)
    
    # 1. 数据收集（如果需要）
    if args.collect_data or not os.path.exists(args.data_path):
        print("📚 步骤1: 收集训练数据")
        collector = LegalDataCollector()
        collector.create_synthetic_data()
        collector.process_data()
        collector.save_data(os.path.basename(args.data_path))
        print()
    
    # 2. 模型训练
    print("🚀 步骤2: 开始模型训练")
    
    # 训练配置
    config = {
        'model_name': 'bert-base-chinese',
        'num_labels': 10,
        'max_length': args.max_length,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate,
        'warmup_steps': 500,
        'output_dir': args.output_dir
    }
    
    # 创建训练器
    trainer = LegalBERTTrainer(config)
    
    # 设置模型
    trainer.setup_model()
    
    # 准备数据
    train_dataset, val_dataset = trainer.prepare_data(args.data_path)
    
    # 开始训练
    trainer.train(train_dataset, val_dataset)
    
    print("\n✅ 训练完成！")
    print(f"📁 模型保存在: {args.output_dir}")
    print("\n🧪 测试模型:")
    
    # 测试预测
    test_cases = [
        "合同双方应当按照约定履行义务",
        "用人单位应当为劳动者缴纳社会保险",
        "侵犯他人知识产权应当承担法律责任"
    ]
    
    for text in test_cases:
        try:
            result = trainer.predict(text)
            print(f"文本: {text}")
            print(f"预测类别: {result['predicted_class']}")
            print(f"置信度: {result['confidence']:.4f}")
            print("-" * 50)
        except Exception as e:
            print(f"预测失败: {e}")

if __name__ == "__main__":
    main()






