# 回归测试网络（Regtest）设置指南

## 什么是 Regtest 网络？

回归测试网络（Regression Test Network，简称 Regtest）是比特币核心提供的一个本地测试环境，专门用于开发和测试。与主网络（Mainnet）和测试网络（Testnet）不同，Regtest 网络具有以下特点：

- **完全本地化**：不需要连接到外部网络
- **可控制挖矿**：可以随时生成区块
- **快速同步**：无需下载整个区块链
- **安全测试**：不会影响真实资金

## 环境配置步骤

### 1. 创建专用目录
```bash
# 创建学习专用目录
mkdir -p ~/bitcoin_learning
cd ~/bitcoin_learning

# 创建数据目录
mkdir -p data/regtest
```

### 2. 创建配置文件
```bash
# 创建比特币核心配置文件
nano ~/bitcoin_learning/bitcoin.conf
```

添加以下配置内容：
```ini
# 网络配置
regtest=1
server=1
rpcuser=bitcoin
rpcpassword=bitcoin
rpcport=18443
rpcallowip=127.0.0.1

# 数据目录
datadir=/home/[用户名]/bitcoin_learning/data

# 性能优化
dbcache=100
maxmempool=50
maxconnections=10

# 日志配置
debug=1
logtimestamps=1

# 挖矿配置
blockmintxfee=0.00001
```

### 3. 启动比特币核心
```bash
# 启动比特币核心守护进程
bitcoind -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -daemon

# 检查是否启动成功
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getblockchaininfo
```

### 4. 验证网络状态
```bash
# 检查网络信息
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getnetworkinfo

# 检查区块链信息
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getblockchaininfo

# 检查节点状态
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getinfo
```

## 便捷脚本设置

### 1. 创建启动脚本
```bash
nano ~/bitcoin_learning/start_bitcoin.sh
```

添加以下内容：
```bash
#!/bin/bash

# 比特币学习环境启动脚本
CONFIG_FILE="/home/[用户名]/bitcoin_learning/bitcoin.conf"
DATA_DIR="/home/[用户名]/bitcoin_learning/data"

echo "启动比特币核心回归测试网络..."

# 检查是否已经在运行
if pgrep -f "bitcoind.*regtest" > /dev/null; then
    echo "比特币核心已在运行"
    exit 1
fi

# 启动比特币核心
bitcoind -conf=$CONFIG_FILE -daemon

# 等待启动完成
sleep 3

# 检查启动状态
if bitcoin-cli -conf=$CONFIG_FILE getblockchaininfo > /dev/null 2>&1; then
    echo "✅ 比特币核心启动成功"
    echo "📊 网络信息："
    bitcoin-cli -conf=$CONFIG_FILE getnetworkinfo | grep -E "(version|subversion)"
    echo "📈 区块链信息："
    bitcoin-cli -conf=$CONFIG_FILE getblockchaininfo | grep -E "(chain|blocks|verificationprogress)"
else
    echo "❌ 比特币核心启动失败"
    exit 1
fi
```

### 2. 创建停止脚本
```bash
nano ~/bitcoin_learning/stop_bitcoin.sh
```

添加以下内容：
```bash
#!/bin/bash

# 比特币学习环境停止脚本
CONFIG_FILE="/home/[用户名]/bitcoin_learning/bitcoin.conf"

echo "停止比特币核心..."

# 发送停止信号
bitcoin-cli -conf=$CONFIG_FILE stop

# 等待停止完成
sleep 3

# 检查是否已停止
if ! pgrep -f "bitcoind.*regtest" > /dev/null; then
    echo "✅ 比特币核心已停止"
else
    echo "⚠️  比特币核心可能仍在运行，请手动检查"
fi
```

### 3. 创建状态检查脚本
```bash
nano ~/bitcoin_learning/check_status.sh
```

添加以下内容：
```bash
#!/bin/bash

# 比特币学习环境状态检查脚本
CONFIG_FILE="/home/[用户名]/bitcoin_learning/bitcoin.conf"

echo "🔍 检查比特币核心状态..."

# 检查进程
if pgrep -f "bitcoind.*regtest" > /dev/null; then
    echo "✅ 比特币核心正在运行"
    
    # 获取网络信息
    echo "📊 网络信息："
    bitcoin-cli -conf=$CONFIG_FILE getnetworkinfo | jq -r '.version, .subversion'
    
    # 获取区块链信息
    echo "📈 区块链信息："
    blockchain_info=$(bitcoin-cli -conf=$CONFIG_FILE getblockchaininfo)
    echo "链: $(echo $blockchain_info | jq -r '.chain')"
    echo "区块数: $(echo $blockchain_info | jq -r '.blocks')"
    echo "同步进度: $(echo $blockchain_info | jq -r '.verificationprogress')"
    
    # 获取钱包信息
    echo "💰 钱包信息："
    bitcoin-cli -conf=$CONFIG_FILE listwallets
else
    echo "❌ 比特币核心未运行"
fi
```

### 4. 设置脚本权限
```bash
chmod +x ~/bitcoin_learning/*.sh
```

## 环境验证

### 1. 基本功能测试
```bash
# 测试 RPC 连接
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf help

# 测试网络信息
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getnetworkinfo

# 测试区块链信息
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getblockchaininfo
```

### 2. 挖矿功能测试
```bash
# 生成一个测试地址
ADDRESS=$(bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getnewaddress)

# 挖一个区块
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf generatetoaddress 1 $ADDRESS

# 检查余额
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getbalance
```

## 常见问题解决

### 问题1：启动失败
**可能原因：**
- 端口被占用
- 配置文件错误
- 权限问题

**解决方案：**
```bash
# 检查端口占用
netstat -tlnp | grep :18443

# 检查配置文件语法
bitcoind -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -check

# 检查权限
ls -la /home/[用户名]/bitcoin_learning/
```

### 问题2：RPC 连接失败
**可能原因：**
- RPC 用户/密码错误
- 网络配置问题

**解决方案：**
```bash
# 检查 RPC 配置
grep -E "(rpcuser|rpcpassword|rpcport)" /home/[用户名]/bitcoin_learning/bitcoin.conf

# 测试 RPC 连接
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcuser=bitcoin -rpcpassword=bitcoin getinfo
```

### 问题3：数据目录问题
**可能原因：**
- 数据目录不存在
- 权限不足

**解决方案：**
```bash
# 创建数据目录
mkdir -p /home/[用户名]/bitcoin_learning/data

# 设置权限
chmod 755 /home/[用户名]/bitcoin_learning/data

# 检查数据目录
ls -la /home/[用户名]/bitcoin_learning/data/
```

## 环境清理

### 重置测试环境
```bash
# 停止比特币核心
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf stop

# 删除数据目录
rm -rf /home/[用户名]/bitcoin_learning/data/regtest

# 重新启动
bitcoind -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -daemon
```

### 完全清理
```bash
# 停止所有比特币进程
pkill -f bitcoind

# 删除所有数据
rm -rf /home/[用户名]/bitcoin_learning/data

# 重新创建环境
mkdir -p /home/[用户名]/bitcoin_learning/data
```

## 下一步
环境配置完成后，请继续阅读 [钱包操作指南](../03_wallet_operations/wallet_creation.md) 来学习钱包的创建和管理。

## 相关链接
- [Bitcoin Core 配置文档](https://bitcoincore.org/en/doc/0.21.0/rpc/)
- [回归测试网络文档](https://bitcoincore.org/en/doc/0.21.0/rpc/network/generatetoaddress/)
- [RPC 接口文档](https://bitcoincore.org/en/doc/0.21.0/rpc/)





