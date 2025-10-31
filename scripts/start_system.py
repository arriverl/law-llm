#!/usr/bin/env python3
"""
系统启动脚本
一键启动整个AI法律服务生态链系统
"""
import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_requirements():
    """检查系统要求"""
    print("检查系统要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要的目录
    required_dirs = ["backend", "frontend", "scripts"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"❌ 缺少目录: {dir_name}")
            return False
        print(f"✅ 目录存在: {dir_name}")
    
    return True

def install_backend_dependencies():
    """安装后端依赖"""
    print("\n安装后端依赖...")
    try:
        os.chdir("backend")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 后端依赖安装成功")
            return True
        else:
            print(f"❌ 后端依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 后端依赖安装失败: {e}")
        return False
    finally:
        os.chdir("..")

def install_frontend_dependencies():
    """安装前端依赖"""
    print("\n安装前端依赖...")
    try:
        os.chdir("frontend")
        result = subprocess.run(["npm", "install"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 前端依赖安装成功")
            return True
        else:
            print(f"❌ 前端依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 前端依赖安装失败: {e}")
        return False
    finally:
        os.chdir("..")

def setup_database():
    """设置数据库"""
    print("\n设置数据库...")
    try:
        # 运行数据库初始化脚本
        result = subprocess.run([sys.executable, "scripts/setup_database.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 数据库设置成功")
            return True
        else:
            print(f"❌ 数据库设置失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("\n启动后端服务...")
    try:
        os.chdir("backend")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        print("✅ 后端服务启动成功 (PID: {})".format(process.pid))
        return process
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None
    finally:
        os.chdir("..")

def start_frontend():
    """启动前端服务"""
    print("\n启动前端服务...")
    try:
        os.chdir("frontend")
        process = subprocess.Popen(["npm", "start"])
        print("✅ 前端服务启动成功 (PID: {})".format(process.pid))
        return process
    except Exception as e:
        print(f"❌ 前端服务启动失败: {e}")
        return None
    finally:
        os.chdir("..")

def collect_data():
    """采集数据"""
    print("\n开始数据采集...")
    try:
        result = subprocess.run([sys.executable, "scripts/data_collection.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 数据采集完成")
            return True
        else:
            print(f"❌ 数据采集失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 数据采集失败: {e}")
        return False

def wait_for_services():
    """等待服务启动"""
    print("\n等待服务启动...")
    time.sleep(5)
    
    # 检查后端服务
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
        else:
            print("❌ 后端服务响应异常")
    except Exception as e:
        print(f"❌ 后端服务检查失败: {e}")
    
    # 检查前端服务
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务运行正常")
        else:
            print("❌ 前端服务响应异常")
    except Exception as e:
        print(f"❌ 前端服务检查失败: {e}")

def show_system_info():
    """显示系统信息"""
    print("\n" + "="*60)
    print("🎉 AI法律服务生态链系统启动成功!")
    print("="*60)
    print("\n📋 系统访问信息:")
    print("  后端API: http://localhost:8000")
    print("  前端界面: http://localhost:3000")
    print("  API文档: http://localhost:8000/docs")
    print("  管理后台: http://localhost:8000/admin")
    
    print("\n👤 默认用户账号:")
    print("  管理员: admin / admin123")
    print("  律师: lawyer1 / lawyer123")
    print("  企业: enterprise1 / enterprise123")
    print("  用户: user1 / user123")
    
    print("\n🔧 系统功能:")
    print("  ✅ 智能法律咨询")
    print("  ✅ 法律知识库管理")
    print("  ✅ 生态协同管理")
    print("  ✅ 数据分析仪表盘")
    print("  ✅ AI模型集成")
    
    print("\n📚 技术栈:")
    print("  后端: FastAPI + Python + PostgreSQL")
    print("  前端: React + TypeScript + Ant Design")
    print("  AI模型: DeepSeek R1 + BERT")
    print("  数据库: PostgreSQL + Redis")
    
    print("\n🚀 下一步操作:")
    print("  1. 访问 http://localhost:3000 开始使用")
    print("  2. 使用默认账号登录系统")
    print("  3. 体验智能法律咨询功能")
    print("  4. 管理法律知识库")
    print("  5. 配置生态合作伙伴")
    
    print("\n⚠️  注意事项:")
    print("  - 请确保数据库服务正在运行")
    print("  - 请确保Redis服务正在运行")
    print("  - 如需配置AI模型，请编辑 .env 文件")
    print("  - 按 Ctrl+C 停止所有服务")
    
    print("\n" + "="*60)

def signal_handler(sig, frame):
    """信号处理器"""
    print("\n\n🛑 正在停止系统...")
    sys.exit(0)

def main():
    """主函数"""
    print("🚀 AI法律服务生态链系统启动器")
    print("="*60)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 1. 检查系统要求
        if not check_requirements():
            print("❌ 系统要求检查失败，请解决上述问题后重试")
            return
        
        # 2. 安装后端依赖
        if not install_backend_dependencies():
            print("❌ 后端依赖安装失败，请检查网络连接和Python环境")
            return
        
        # 3. 安装前端依赖
        if not install_frontend_dependencies():
            print("❌ 前端依赖安装失败，请检查Node.js环境")
            return
        
        # 4. 设置数据库
        if not setup_database():
            print("❌ 数据库设置失败，请检查数据库连接")
            return
        
        # 5. 采集数据
        collect_data()
        
        # 6. 启动后端服务
        backend_process = start_backend()
        if not backend_process:
            print("❌ 后端服务启动失败")
            return
        
        # 7. 启动前端服务
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ 前端服务启动失败")
            return
        
        # 8. 等待服务启动
        wait_for_services()
        
        # 9. 显示系统信息
        show_system_info()
        
        # 10. 保持运行
        print("\n⏳ 系统运行中，按 Ctrl+C 停止...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止系统...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ 系统已停止")
    
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        return

if __name__ == "__main__":
    main()






