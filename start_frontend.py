#!/usr/bin/env python3
"""
AI法律服务生态链系统 - 前端启动脚本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_node():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js未安装")
            return False
    except FileNotFoundError:
        print("❌ Node.js未安装")
        return False

def check_npm():
    """检查npm是否安装"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ npm检查失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ npm未找到，请检查PATH环境变量")
        return False
    except Exception as e:
        print(f"❌ npm检查异常: {e}")
        return False

def install_dependencies():
    """安装前端依赖"""
    print("📦 安装前端依赖...")
    try:
        result = subprocess.run(["npm", "install"], cwd="frontend", capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print(f"❌ 依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 启动AI法律服务生态链系统前端...")
    print("=" * 50)
    
    # 检查Node.js和npm
    if not check_node() or not check_npm():
        print("请先安装Node.js和npm")
        print("下载地址: https://nodejs.org/")
        sys.exit(1)
    
    # 检查package.json是否存在
    if not Path("frontend/package.json").exists():
        print("❌ 未找到package.json文件")
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    print("=" * 50)
    print("🎯 启动前端开发服务器...")
    
    # 启动前端服务器
    try:
        os.chdir("frontend")
        subprocess.run(["npm", "start"])
    except KeyboardInterrupt:
        print("\n👋 前端服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()





