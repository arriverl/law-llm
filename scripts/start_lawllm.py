#!/usr/bin/env python3
"""
启动 LawLLM-7B 服务
"""
import os
import sys
import subprocess
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
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

def main():
    """主函数"""
    logger.info("🌏 启动 LawLLM-7B 服务")
    logger.info("=" * 50)
    logger.info("参考项目: https://github.com/FudanDISC/DISC-LawLLM")
    
    start_time = datetime.now()
    
    try:
        # 1. 检查环境
        logger.info("\n1. 检查环境...")
        if not os.path.exists("requirements.txt"):
            logger.error("未找到requirements.txt文件")
            return
        
        # 2. 安装依赖
        logger.info("\n2. 安装 LawLLM-7B 依赖...")
        success = run_command("pip install -r requirements.txt", "安装Python依赖")
        if not success:
            logger.error("依赖安装失败，请手动安装")
            return
        
        # 3. 检查 vLLM 安装
        logger.info("\n3. 检查 vLLM 安装...")
        try:
            import vllm
            logger.info(f"✅ vLLM 版本: {vllm.__version__}")
        except ImportError:
            logger.error("❌ vLLM 未安装，请先安装: pip install vllm")
            return
        
        # 4. 检查 transformers 安装
        logger.info("\n4. 检查 transformers 安装...")
        try:
            import transformers
            logger.info(f"✅ transformers 版本: {transformers.__version__}")
        except ImportError:
            logger.error("❌ transformers 未安装")
            return
        
        # 5. 测试 LawLLM-7B 模型
        logger.info("\n5. 测试 LawLLM-7B 模型...")
        success = run_command("python scripts/test_lawllm.py", "测试LawLLM-7B模型")
        if not success:
            logger.error("模型测试失败")
            return
        
        # 6. 启动后端服务
        logger.info("\n6. 启动后端服务...")
        logger.info("请手动运行以下命令启动后端服务:")
        logger.info("cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
        # 7. 完成
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        logger.info("\n🎉 LawLLM-7B 服务启动完成!")
        logger.info(f"⏱️ 总耗时: {total_time:.2f} 秒")
        logger.info("\n📖 使用说明:")
        logger.info("1. 后端API: http://localhost:8000")
        logger.info("2. API文档: http://localhost:8000/docs")
        logger.info("3. 法律咨询接口: POST /api/legal-ai/consult")
        logger.info("4. 法律分析接口: POST /api/legal-ai/analyze")
        logger.info("5. 模型状态接口: GET /api/legal-ai/model-status")
        
        logger.info("\n🔧 测试命令:")
        logger.info("curl -X POST http://localhost:8000/api/legal-ai/consult \\")
        logger.info("  -H 'Content-Type: application/json' \\")
        logger.info("  -d '{\"question\": \"生产销售假冒伪劣商品罪如何判刑？\"}'")
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise

if __name__ == "__main__":
    main()






