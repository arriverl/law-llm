# Linux 系统比特币核心安装指南

## 系统要求
- Ubuntu 18.04+ / Debian 10+ / CentOS 7+ / Fedora 30+
- 至少 10GB 可用磁盘空间
- 4GB RAM（推荐 8GB 或更多）
- 稳定的网络连接

## Ubuntu/Debian 系统安装

### 方法一：使用官方 PPA（推荐）

#### 1. 添加官方 PPA
```bash
# 更新包列表
sudo apt update

# 安装必要的依赖
sudo apt install software-properties-common

# 添加比特币核心 PPA
sudo add-apt-repository ppa:bitcoin/bitcoin

# 更新包列表
sudo apt update
```

#### 2. 安装比特币核心
```bash
sudo apt install bitcoind bitcoin-cli bitcoin-tx
```

### 方法二：从源码编译

#### 1. 安装依赖
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装编译依赖
sudo apt install build-essential libtool autotools-dev automake pkg-config bsdmainutils python3

# 安装比特币核心依赖
sudo apt install libssl-dev libevent-dev libboost-system-dev libboost-filesystem-dev libboost-chrono-dev libboost-program-options-dev libboost-test-dev libboost-thread-dev

# 安装 Berkeley DB
sudo apt install libdb-dev libdb++-dev

# 安装其他依赖
sudo apt install libsqlite3-dev libminiupnpc-dev libnatpmp-dev libzmq3-dev libqrencode-dev
```

#### 2. 编译比特币核心
```bash
# 克隆源码
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin

# 生成配置脚本
./autogen.sh

# 配置编译选项
./configure --enable-upnp-default

# 编译（使用多核加速）
make -j$(nproc)

# 安装
sudo make install
```

## CentOS/RHEL/Fedora 系统安装

### 方法一：使用 EPEL 仓库

#### 1. 安装 EPEL 仓库
```bash
# CentOS/RHEL 7
sudo yum install epel-release

# CentOS/RHEL 8
sudo dnf install epel-release

# Fedora
sudo dnf install epel-release
```

#### 2. 安装比特币核心
```bash
# CentOS/RHEL 7
sudo yum install bitcoind bitcoin-cli

# CentOS/RHEL 8/Fedora
sudo dnf install bitcoind bitcoin-cli
```

### 方法二：从源码编译

#### 1. 安装依赖
```bash
# 安装开发工具
sudo yum groupinstall "Development Tools"
# 或
sudo dnf groupinstall "Development Tools"

# 安装依赖包
sudo yum install libevent-devel boost-devel openssl-devel libdb4-devel libdb4-cxx-devel
# 或
sudo dnf install libevent-devel boost-devel openssl-devel libdb4-devel libdb4-cxx-devel
```

#### 2. 编译安装
```bash
# 克隆源码
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin

# 生成配置脚本
./autogen.sh

# 配置编译选项
./configure

# 编译
make -j$(nproc)

# 安装
sudo make install
```

## Arch Linux 安装

### 使用 AUR
```bash
# 安装 AUR 助手
sudo pacman -S base-devel git

# 安装比特币核心
yay -S bitcoin-core
# 或
paru -S bitcoin-core
```

### 从源码编译
```bash
# 安装依赖
sudo pacman -S base-devel boost libevent openssl db

# 克隆源码
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin

# 编译安装
./autogen.sh
./configure
make -j$(nproc)
sudo make install
```

## 验证安装

### 1. 检查版本
```bash
bitcoind --version
bitcoin-cli --version
```

### 2. 检查帮助信息
```bash
bitcoind --help
bitcoin-cli --help
```

## 配置比特币核心

### 1. 创建数据目录
```bash
mkdir -p ~/.bitcoin
```

### 2. 创建配置文件
```bash
nano ~/.bitcoin/bitcoin.conf
```

添加以下配置：
```ini
# 网络配置
regtest=1
server=1
rpcuser=bitcoin
rpcpassword=bitcoin
rpcport=18443
rpcallowip=127.0.0.1

# 性能优化
dbcache=100
maxmempool=50

# 日志配置
debug=1
```

### 3. 设置权限
```bash
chmod 600 ~/.bitcoin/bitcoin.conf
```

## 创建系统服务（可选）

### 1. 创建服务文件
```bash
sudo nano /etc/systemd/system/bitcoind.service
```

添加以下内容：
```ini
[Unit]
Description=Bitcoin Core daemon
After=network.target

[Service]
Type=forking
User=bitcoin
Group=bitcoin
ExecStart=/usr/local/bin/bitcoind -daemon -conf=/home/bitcoin/.bitcoin/bitcoin.conf
ExecStop=/usr/local/bin/bitcoin-cli -conf=/home/bitcoin/.bitcoin/bitcoin.conf stop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. 创建专用用户
```bash
sudo useradd -m -s /bin/bash bitcoin
sudo mkdir -p /home/bitcoin/.bitcoin
sudo chown -R bitcoin:bitcoin /home/bitcoin/.bitcoin
```

### 3. 启用服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable bitcoind
sudo systemctl start bitcoind
```

## 常见问题解决

### 问题1：编译错误
**解决方案：**
```bash
# 确保所有依赖已安装
sudo apt install build-essential libtool autotools-dev automake pkg-config bsdmainutils python3 libssl-dev libevent-dev libboost-system-dev libboost-filesystem-dev libboost-chrono-dev libboost-program-options-dev libboost-test-dev libboost-thread-dev libdb-dev libdb++-dev libsqlite3-dev libminiupnpc-dev libnatpmp-dev libzmq3-dev libqrencode-dev

# 清理并重新编译
make clean
./configure
make -j$(nproc)
```

### 问题2：权限问题
**解决方案：**
```bash
# 检查文件权限
ls -la ~/.bitcoin/

# 修复权限
chmod 600 ~/.bitcoin/bitcoin.conf
chmod 700 ~/.bitcoin/
```

### 问题3：端口被占用
**解决方案：**
```bash
# 查看端口占用
sudo netstat -tlnp | grep :8332
sudo netstat -tlnp | grep :8333

# 结束占用进程
sudo kill -9 [进程ID]
```

### 问题4：依赖缺失
**解决方案：**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -f

# CentOS/RHEL
sudo yum update && sudo yum install -y

# 重新安装比特币核心
sudo apt remove bitcoind bitcoin-cli
sudo apt install bitcoind bitcoin-cli
```

## 性能优化

### 1. 系统优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化网络参数
echo "net.core.rmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
```

### 2. 比特币核心优化
```bash
# 在 bitcoin.conf 中添加
dbcache=200
maxmempool=100
maxconnections=50
```

## 安全建议

### 1. 防火墙配置
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 8333
sudo ufw allow 8332

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8333/tcp
sudo firewall-cmd --permanent --add-port=8332/tcp
sudo firewall-cmd --reload
```

### 2. 数据备份
```bash
# 创建备份脚本
nano ~/backup_bitcoin.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/bitcoin/backups"
mkdir -p $BACKUP_DIR
cp ~/.bitcoin/wallet.dat $BACKUP_DIR/wallet_$DATE.dat
echo "Backup completed: wallet_$DATE.dat"
```

```bash
chmod +x ~/backup_bitcoin.sh
```

## 下一步
安装完成后，请继续阅读 [环境配置指南](../02_environment_setup/regtest_setup.md) 来设置测试网络。

## 相关链接
- [Bitcoin Core 官方文档](https://bitcoincore.org/en/doc/)
- [Ubuntu 安装指南](https://github.com/bitcoin/bitcoin/blob/master/doc/build-unix.md)
- [Linux 开发环境设置](https://github.com/bitcoin/bitcoin/blob/master/doc/build-unix.md)





