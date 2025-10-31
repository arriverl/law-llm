# Windows 系统比特币核心安装指南

## 系统要求
- Windows 10 或更高版本
- 至少 10GB 可用磁盘空间
- 4GB RAM（推荐 8GB 或更多）
- 稳定的网络连接

## 方法一：官方二进制文件安装（推荐）

### 1. 下载比特币核心
1. 访问 [Bitcoin Core 官方下载页面](https://bitcoincore.org/en/download/)
2. 选择适合您系统的版本（64位或32位）
3. 下载 `.exe` 安装文件

### 2. 安装步骤
1. 双击下载的 `.exe` 文件
2. 按照安装向导进行安装
3. 选择安装路径（建议使用默认路径）
4. 完成安装

### 3. 验证安装
打开命令提示符（cmd）或 PowerShell，输入：
```bash
bitcoind --version
bitcoin-cli --version
```

如果显示版本信息，说明安装成功。

## 方法二：从源码编译（高级用户）

### 1. 安装依赖
```bash
# 安装 Visual Studio Build Tools
# 下载并安装 Visual Studio Community 或 Build Tools

# 安装 vcpkg 包管理器
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install
```

### 2. 安装必要的库
```bash
vcpkg install boost-system:x64-windows
vcpkg install boost-filesystem:x64-windows
vcpkg install boost-thread:x64-windows
vcpkg install boost-chrono:x64-windows
vcpkg install boost-program-options:x64-windows
vcpkg install boost-test:x64-windows
vcpkg install libevent:x64-windows
vcpkg install sqlite3:x64-windows
```

### 3. 编译比特币核心
```bash
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin
mkdir build
cd build
cmake -DCMAKE_TOOLCHAIN_FILE=[vcpkg root]/scripts/buildsystems/vcpkg.cmake ..
cmake --build . --config Release
```

## 方法三：使用包管理器

### 使用 Chocolatey
```bash
# 安装 Chocolatey（如果未安装）
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 安装比特币核心
choco install bitcoin-core
```

### 使用 Scoop
```bash
# 安装 Scoop（如果未安装）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# 安装比特币核心
scoop install bitcoin-core
```

## 配置环境变量

### 1. 添加到 PATH
1. 打开"系统属性" → "高级" → "环境变量"
2. 在"系统变量"中找到"Path"
3. 添加比特币核心的安装路径（通常是 `C:\Program Files\Bitcoin\daemon\` 和 `C:\Program Files\Bitcoin\daemon\`）

### 2. 验证环境变量
重新打开命令提示符，输入：
```bash
where bitcoind
where bitcoin-cli
```

## 常见问题解决

### 问题1：找不到 bitcoind 命令
**解决方案：**
- 检查安装路径是否正确
- 确认环境变量已正确设置
- 重启命令提示符

### 问题2：权限不足
**解决方案：**
- 以管理员身份运行命令提示符
- 检查防火墙设置
- 确认杀毒软件未阻止程序运行

### 问题3：端口被占用
**解决方案：**
```bash
# 查看端口占用情况
netstat -ano | findstr :8332
netstat -ano | findstr :8333

# 结束占用进程（替换 PID）
taskkill /PID [进程ID] /F
```

## 下一步
安装完成后，请继续阅读 [环境配置指南](../02_environment_setup/regtest_setup.md) 来设置测试网络。

## 相关链接
- [Bitcoin Core 官方文档](https://bitcoincore.org/en/doc/)
- [Bitcoin Core GitHub 仓库](https://github.com/bitcoin/bitcoin)
- [Windows 开发环境设置指南](https://github.com/bitcoin/bitcoin/blob/master/doc/build-windows.md)





