#!/usr/bin/env python3
"""
一键启动DISC-LawLLM BERT模型训练
包含数据收集和模型训练的完整流程
"""
import os
import sys
import asyncio
import subprocess
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_command(command, description):
    """运行命令"""
    logger.info(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description}失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False

async def main():
    """主函数"""
    logger.info("🌏 一键启动DISC-LawLLM BERT模型训练")
    logger.info("=" * 60)
    logger.info("参考项目: https://github.com/FudanDISC/DISC-LawLLM")
    
    start_time = datetime.now()
    
    try:
        # 1. 检查环境
        logger.info("\n1. 检查环境...")
        if not os.path.exists("requirements.txt"):
            logger.error("未找到requirements.txt文件")
            return
        
        # 2. 安装依赖
        logger.info("\n2. 安装依赖...")
        success = await run_command("pip install -r requirements.txt", "安装Python依赖")
        if not success:
            logger.error("依赖安装失败，请手动安装")
            return
        
        # 3. 收集数据
        logger.info("\n3. 收集粤港澳大湾区法律数据...")
        success = await run_command("python scripts/collect_disc_law_data.py", "收集法律数据")
        if not success:
            logger.error("数据收集失败")
            return
        
        # 4. 训练模型
        logger.info("\n4. 训练DISC-LawLLM BERT模型...")
        success = await run_command("python scripts/train_disc_law_bert.py", "训练BERT模型")
        if not success:
            logger.error("模型训练失败")
            return
        
        # 5. 完成
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        logger.info("\n🎉 DISC-LawLLM BERT模型训练完成!")
        logger.info(f"⏱️ 总耗时: {total_time:.2f} 秒")
        logger.info("📁 模型保存在: ./models/disc_law_bert")
        logger.info("📚 数据保存在: ./data/disc_law_data")
        
        # 6. 显示使用说明
        logger.info("\n📖 使用说明:")
        logger.info("1. 模型文件位置: ./models/disc_law_bert")
        logger.info("2. 训练数据位置: ./data/disc_law_data")
        logger.info("3. 使用示例:")
        logger.info("   from backend.app.services.disc_law_bert import DISCLawBERT")
        logger.info("   model = DISCLawBERT.load_model('./models/disc_law_bert')")
        logger.info("   results = model.predict(['根据合同法规定...'])")
        
    except Exception as e:
        logger.error(f"训练流程失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())






