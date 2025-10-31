# 钱包创建与管理指南

## 什么是比特币钱包？

比特币钱包实际上是一个存储私钥的容器，而不是存储比特币本身。私钥是访问比特币的关键，拥有私钥就拥有对应地址上的比特币。

### 钱包的核心概念
- **私钥（Private Key）**：用于签名交易，证明资产所有权
- **公钥（Public Key）**：由私钥生成，用于生成地址
- **地址（Address）**：由公钥生成，用于接收比特币
- **助记词（Mnemonic）**：用于恢复钱包的单词序列

## 钱包类型

### 1. 软件钱包
- **桌面钱包**：Bitcoin Core、Electrum
- **移动钱包**：Blockstream Green、BlueWallet
- **网页钱包**：Blockchain.info、Coinbase

### 2. 硬件钱包
- **Ledger**：Nano S、Nano X
- **Trezor**：Model T、One
- **KeepKey**：硬件钱包

### 3. 纸钱包
- 离线生成的私钥和地址
- 最高安全性，但使用不便

## 在 Regtest 网络中创建钱包

### 1. 创建第一个钱包
```bash
# 创建钱包1
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf createwallet "wallet1"

# 验证钱包创建
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf listwallets
```

### 2. 创建第二个钱包
```bash
# 创建钱包2
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf createwallet "wallet2"

# 验证钱包创建
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf listwallets
```

### 3. 钱包管理命令
```bash
# 列出所有钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf listwallets

# 加载钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf loadwallet "wallet1"

# 卸载钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf unloadwallet "wallet1"

# 获取钱包信息
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getwalletinfo
```

## 地址生成与管理

### 1. 生成新地址
```bash
# 为钱包1生成地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress

# 为钱包2生成地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet2 getnewaddress
```

### 2. 地址类型
```bash
# 生成不同类型的地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress "" "bech32"  # Bech32 地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress "" "p2sh-segwit"  # P2SH-SegWit 地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress "" "legacy"  # 传统地址
```

### 3. 地址验证
```bash
# 验证地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf validateaddress "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

# 获取地址信息
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf getaddressinfo "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
```

## 完整钱包操作脚本

### 1. 钱包创建脚本
```bash
#!/bin/bash
# 钱包创建和管理脚本

CONFIG_FILE="/home/[用户名]/bitcoin_learning/bitcoin.conf"

echo "🔐 比特币钱包管理脚本"
echo "================================"

# 检查比特币核心是否运行
if ! bitcoin-cli -conf="$CONFIG_FILE" getblockchaininfo > /dev/null 2>&1; then
    echo "❌ 比特币核心未运行，请先启动"
    exit 1
fi

# 创建钱包1
echo "📝 创建钱包1..."
if bitcoin-cli -conf="$CONFIG_FILE" createwallet "wallet1" > /dev/null 2>&1; then
    echo "✅ 钱包1创建成功"
else
    echo "⚠️  钱包1可能已存在"
fi

# 创建钱包2
echo "📝 创建钱包2..."
if bitcoin-cli -conf="$CONFIG_FILE" createwallet "wallet2" > /dev/null 2>&1; then
    echo "✅ 钱包2创建成功"
else
    echo "⚠️  钱包2可能已存在"
fi

# 生成地址
echo "📍 生成地址..."
WALLET1_ADDRESS=$(bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet1 getnewaddress)
WALLET2_ADDRESS=$(bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet2 getnewaddress)

echo "钱包1地址: $WALLET1_ADDRESS"
echo "钱包2地址: $WALLET2_ADDRESS"

# 保存地址到文件
echo "WALLET1_ADDRESS=$WALLET1_ADDRESS" > /home/[用户名]/bitcoin_learning/addresses.env
echo "WALLET2_ADDRESS=$WALLET2_ADDRESS" >> /home/[用户名]/bitcoin_learning/addresses.env

echo "✅ 地址已保存到 addresses.env"
```

### 2. 钱包状态检查脚本
```bash
#!/bin/bash
# 钱包状态检查脚本

CONFIG_FILE="/home/[用户名]/bitcoin_learning/bitcoin.conf"

echo "🔍 钱包状态检查"
echo "================================"

# 检查钱包列表
echo "📋 钱包列表："
bitcoin-cli -conf="$CONFIG_FILE" listwallets

# 检查钱包1状态
echo "💰 钱包1状态："
if bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet1 getwalletinfo > /dev/null 2>&1; then
    echo "✅ 钱包1已加载"
    echo "余额: $(bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet1 getbalance) BTC"
    echo "地址数量: $(bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet1 getaddressesbylabel '' | jq length)"
else
    echo "❌ 钱包1未加载"
fi

# 检查钱包2状态
echo "💰 钱包2状态："
if bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet2 getwalletinfo > /dev/null 2>&1; then
    echo "✅ 钱包2已加载"
    echo "余额: $(bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet2 getbalance) BTC"
    echo "地址数量: $(bitcoin-cli -conf="$CONFIG_FILE" -rpcwallet=wallet2 getaddressesbylabel '' | jq length)"
else
    echo "❌ 钱包2未加载"
fi
```

## 钱包安全最佳实践

### 1. 私钥管理
```bash
# 导出私钥（仅用于学习，生产环境请谨慎）
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 dumpprivkey "地址"

# 导入私钥
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 importprivkey "私钥"
```

### 2. 钱包备份
```bash
# 备份钱包文件
cp /home/[用户名]/bitcoin_learning/data/regtest/wallets/wallet1/wallet.dat /home/[用户名]/bitcoin_learning/backups/wallet1_$(date +%Y%m%d).dat

# 导出钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 dumpwallet /home/[用户名]/bitcoin_learning/backups/wallet1_dump.txt
```

### 3. 钱包加密
```bash
# 加密钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 encryptwallet "密码"

# 解锁钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 walletpassphrase "密码" 60
```

## 常见问题解决

### 问题1：钱包创建失败
**错误信息：** `Wallet already exists`
**解决方案：**
```bash
# 检查钱包是否已存在
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf listwallets

# 如果存在，先卸载再创建
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf unloadwallet "wallet1"
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf createwallet "wallet1"
```

### 问题2：地址生成失败
**错误信息：** `Wallet not loaded`
**解决方案：**
```bash
# 加载钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf loadwallet "wallet1"

# 然后生成地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress
```

### 问题3：权限问题
**错误信息：** `Permission denied`
**解决方案：**
```bash
# 检查文件权限
ls -la /home/[用户名]/bitcoin_learning/data/regtest/wallets/

# 修复权限
chmod -R 755 /home/[用户名]/bitcoin_learning/data/regtest/wallets/
```

## 钱包操作练习

### 练习1：创建多个钱包
```bash
# 创建3个不同的钱包
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf createwallet "alice"
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf createwallet "bob"
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf createwallet "charlie"

# 为每个钱包生成地址
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=alice getnewaddress
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=bob getnewaddress
bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=charlie getnewaddress
```

### 练习2：地址类型比较
```bash
# 生成不同类型的地址
LEGACY_ADDR=$(bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress "" "legacy")
P2SH_ADDR=$(bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress "" "p2sh-segwit")
BECH32_ADDR=$(bitcoin-cli -conf=/home/[用户名]/bitcoin_learning/bitcoin.conf -rpcwallet=wallet1 getnewaddress "" "bech32")

echo "传统地址: $LEGACY_ADDR"
echo "P2SH地址: $P2SH_ADDR"
echo "Bech32地址: $BECH32_ADDR"
```

## 下一步
钱包创建完成后，请继续阅读 [挖矿操作指南](../04_mining_operations/mining_basics.md) 来学习挖矿和UTXO机制。

## 相关链接
- [Bitcoin Core 钱包文档](https://bitcoincore.org/en/doc/0.21.0/rpc/wallet/)
- [地址类型说明](https://bitcoincore.org/en/doc/0.21.0/rpc/wallet/getnewaddress/)
- [钱包安全指南](https://bitcoincore.org/en/doc/0.21.0/rpc/wallet/encryptwallet/)





