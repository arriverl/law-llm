#!/usr/bin/env python3
"""
AI法律服务生态链系统 - 后端启动脚本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import redis
        print("✅ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_database():
    """检查数据库连接"""
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请确保数据库服务正在运行，并检查配置")
        return False

def check_redis():
    """检查Redis连接"""
    try:
        from app.core.config import settings
        import redis
        
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis连接正常")
        return True
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("请确保Redis服务正在运行")
        return False

def create_directories():
    """创建必要的目录"""
    directories = [
        "logs",
        "uploads", 
        "data/knowledge_base",
        "models/bert-legal"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def main():
    """主函数"""
    print("🚀 启动AI法律服务生态链系统后端...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 检查数据库
    if not check_database():
        print("⚠️  数据库连接失败，但将继续启动（某些功能可能不可用）")
    
    # 检查Redis
    if not check_redis():
        print("⚠️  Redis连接失败，但将继续启动（某些功能可能不可用）")
    
    print("=" * 50)
    print("🎯 启动服务器...")
    
    # 启动服务器
    try:
        os.chdir("backend")
        subprocess.run([
            "python", "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()






