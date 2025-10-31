# macOS 系统比特币核心安装指南

## 系统要求
- macOS 10.14 或更高版本
- 至少 10GB 可用磁盘空间
- 4GB RAM（推荐 8GB 或更多）
- 稳定的网络连接

## 方法一：使用 Homebrew 安装（推荐）

### 1. 安装 Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装比特币核心
```bash
brew install bitcoin
```

### 3. 验证安装
```bash
bitcoind --version
bitcoin-cli --version
```

## 方法二：官方二进制文件安装

### 1. 下载比特币核心
1. 访问 [Bitcoin Core 官方下载页面](https://bitcoincore.org/en/download/)
2. 下载适合 macOS 的 `.dmg` 文件

### 2. 安装步骤
1. 双击下载的 `.dmg` 文件
2. 将 Bitcoin Core 拖拽到 Applications 文件夹
3. 从 Applications 文件夹启动 Bitcoin Core

### 3. 添加到 PATH
```bash
# 编辑 shell 配置文件
nano ~/.zshrc  # 或 ~/.bash_profile

# 添加以下行
export PATH="/Applications/Bitcoin-Qt.app/Contents/MacOS:$PATH"

# 重新加载配置
source ~/.zshrc  # 或 source ~/.bash_profile
```

## 方法三：从源码编译

### 1. 安装 Xcode 和命令行工具
```bash
# 安装 Xcode（从 App Store）
# 然后安装命令行工具
xcode-select --install
```

### 2. 安装依赖
```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装必要的依赖
brew install autoconf automake libtool pkg-config boost libevent sqlite
```

### 3. 编译比特币核心
```bash
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin
./autogen.sh
./configure
make
make install
```

## 方法四：使用 MacPorts

### 1. 安装 MacPorts
从 [MacPorts 官网](https://www.macports.org/install.php) 下载并安装

### 2. 安装比特币核心
```bash
sudo port install bitcoin-core
```

## 配置和优化

### 1. 创建比特币数据目录
```bash
mkdir -p ~/Library/Application\ Support/Bitcoin
```

### 2. 创建配置文件
```bash
nano ~/Library/Application\ Support/Bitcoin/bitcoin.conf
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
```

### 3. 设置别名（可选）
```bash
# 编辑 shell 配置文件
nano ~/.zshrc

# 添加以下别名
alias bitcoin-start="bitcoind -regtest -daemon"
alias bitcoin-stop="bitcoin-cli -regtest stop"
alias bitcoin-status="bitcoin-cli -regtest getblockchaininfo"
```

## 常见问题解决

### 问题1：权限被拒绝
**解决方案：**
```bash
# 给比特币核心执行权限
chmod +x /Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt
```

### 问题2：端口被占用
**解决方案：**
```bash
# 查看端口占用
lsof -i :8332
lsof -i :8333

# 结束占用进程
kill -9 [进程ID]
```

### 问题3：Homebrew 安装失败
**解决方案：**
```bash
# 更新 Homebrew
brew update
brew upgrade

# 清理缓存
brew cleanup

# 重新安装
brew uninstall bitcoin
brew install bitcoin
```

### 问题4：编译错误
**解决方案：**
```bash
# 确保 Xcode 命令行工具已安装
xcode-select --install

# 更新依赖
brew update
brew upgrade

# 清理并重新编译
make clean
./configure
make
```

## 性能优化

### 1. 内存优化
```bash
# 在 bitcoin.conf 中添加
dbcache=200
maxmempool=100
```

### 2. 网络优化
```bash
# 在 bitcoin.conf 中添加
maxconnections=50
maxuploadtarget=1000
```

## 安全建议

### 1. 防火墙设置
```bash
# 允许比特币核心通过防火墙
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt
```

### 2. 数据备份
```bash
# 定期备份钱包文件
cp ~/Library/Application\ Support/Bitcoin/wallet.dat ~/Desktop/bitcoin-wallet-backup-$(date +%Y%m%d).dat
```

## 下一步
安装完成后，请继续阅读 [环境配置指南](../02_environment_setup/regtest_setup.md) 来设置测试网络。

## 相关链接
- [Bitcoin Core 官方文档](https://bitcoincore.org/en/doc/)
- [Homebrew 官网](https://brew.sh/)
- [MacPorts 官网](https://www.macports.org/)
- [macOS 开发环境设置指南](https://github.com/bitcoin/bitcoin/blob/master/doc/build-osx.md)





