#!/usr/bin/env python3
"""
MongoDB安装和配置脚本
适用于Windows环境
"""
import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def check_mongodb_installed():
    """检查MongoDB是否已安装"""
    try:
        result = subprocess.run(["mongod", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB已安装")
            print(f"版本: {result.stdout.split()[2]}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ MongoDB未安装")
    return False

def download_mongodb_windows():
    """下载MongoDB for Windows"""
    print("开始下载MongoDB...")
    
    # MongoDB下载URL（社区版）
    mongodb_url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.4-signed.msi"
    download_path = "mongodb-installer.msi"
    
    try:
        print("正在下载MongoDB安装包...")
        urllib.request.urlretrieve(mongodb_url, download_path)
        print("✅ MongoDB安装包下载完成")
        return download_path
    except Exception as e:
        print(f"❌ 下载MongoDB失败: {e}")
        return None

def install_mongodb_windows(installer_path):
    """安装MongoDB on Windows"""
    print("开始安装MongoDB...")
    
    try:
        # 使用msiexec安装MongoDB
        result = subprocess.run([
            "msiexec", "/i", installer_path, "/quiet", "/norestart"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MongoDB安装成功")
            return True
        else:
            print(f"❌ MongoDB安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ MongoDB安装失败: {e}")
        return False

def setup_mongodb_data_directory():
    """设置MongoDB数据目录"""
    print("设置MongoDB数据目录...")
    
    # 创建数据目录
    data_dir = Path("C:/data/db")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建日志目录
    log_dir = Path("C:/data/log")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ 数据目录: {data_dir}")
    print(f"✅ 日志目录: {log_dir}")

def start_mongodb_service():
    """启动MongoDB服务"""
    print("启动MongoDB服务...")
    
    try:
        # 启动MongoDB服务
        result = subprocess.run([
            "net", "start", "MongoDB"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MongoDB服务启动成功")
            return True
        else:
            print(f"❌ MongoDB服务启动失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ MongoDB服务启动失败: {e}")
        return False

def test_mongodb_connection():
    """测试MongoDB连接"""
    print("测试MongoDB连接...")
    
    try:
        # 使用mongo客户端测试连接
        result = subprocess.run([
            "mongo", "--eval", "db.runCommand('ping')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ MongoDB连接测试成功")
            return True
        else:
            print(f"❌ MongoDB连接测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ MongoDB连接测试失败: {e}")
        return False

def create_mongodb_user():
    """创建MongoDB用户"""
    print("创建MongoDB用户...")
    
    try:
        # 创建管理员用户
        create_admin_script = """
        use admin;
        db.createUser({
            user: "law_ai_admin",
            pwd: "law_ai_password",
            roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
        });
        """
        
        with open("create_admin.js", "w") as f:
            f.write(create_admin_script)
        
        result = subprocess.run([
            "mongo", "admin", "create_admin.js"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MongoDB管理员用户创建成功")
            return True
        else:
            print(f"❌ MongoDB用户创建失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ MongoDB用户创建失败: {e}")
        return False

def setup_mongodb_config():
    """设置MongoDB配置"""
    print("设置MongoDB配置...")
    
    # 创建配置文件
    config_content = """
# MongoDB配置文件
storage:
  dbPath: C:/data/db
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: C:/data/log/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: enabled
"""
    
    config_path = Path("mongod.conf")
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print(f"✅ MongoDB配置文件: {config_path.absolute()}")

def main():
    """主函数"""
    print("🚀 MongoDB安装和配置脚本")
    print("=" * 50)
    
    # 检查操作系统
    if platform.system() != "Windows":
        print("❌ 此脚本仅支持Windows系统")
        return
    
    try:
        # 1. 检查MongoDB是否已安装
        if check_mongodb_installed():
            print("MongoDB已安装，跳过安装步骤")
        else:
            # 2. 下载MongoDB
            installer_path = download_mongodb_windows()
            if not installer_path:
                return
            
            # 3. 安装MongoDB
            if not install_mongodb_windows(installer_path):
                return
            
            # 清理安装包
            os.remove(installer_path)
        
        # 4. 设置数据目录
        setup_mongodb_data_directory()
        
        # 5. 设置配置文件
        setup_mongodb_config()
        
        # 6. 启动MongoDB服务
        if not start_mongodb_service():
            print("请手动启动MongoDB服务")
        
        # 7. 测试连接
        if test_mongodb_connection():
            print("✅ MongoDB安装和配置完成!")
            
            print("\n📋 MongoDB连接信息:")
            print("  连接URL: mongodb://localhost:27017")
            print("  数据库名: law_ai_db")
            print("  管理员用户: law_ai_admin")
            print("  管理员密码: law_ai_password")
            
            print("\n🔧 下一步操作:")
            print("  1. 运行: python scripts/setup_database.py")
            print("  2. 启动后端服务: python start_backend.py")
            print("  3. 访问: http://localhost:8000")
        else:
            print("❌ MongoDB连接测试失败，请检查配置")
    
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")

if __name__ == "__main__":
    main()

