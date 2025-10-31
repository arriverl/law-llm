# 区块链知识学习指南 - 从零开始

## 项目概述
本指南将带您从零开始学习区块链技术，通过实际操作比特币核心（Bitcoin Core）来深入理解区块链的工作原理。

## 学习目标
- 理解区块链的基本概念
- 掌握比特币钱包和地址的生成
- 学习挖矿和UTXO机制
- 实践原始交易的构建、签名和广播
- 深入理解比特币交易的生命周期

## 目录结构
```
blockchain_learning_guide/
├── README.md                    # 本文件
├── 01_installation/            # 安装指南
│   ├── windows_installation.md
│   ├── mac_installation.md
│   └── linux_installation.md
├── 02_environment_setup/        # 环境配置
│   ├── regtest_setup.md
│   └── configuration.md
├── 03_wallet_operations/        # 钱包操作
│   ├── wallet_creation.md
│   └── address_generation.md
├── 04_mining_operations/        # 挖矿操作
│   ├── mining_basics.md
│   └── utxo_understanding.md
├── 05_transaction_creation/     # 交易创建
│   ├── raw_transaction.md
│   └── input_output.md
├── 06_transaction_signing/      # 交易签名
│   ├── digital_signature.md
│   └── private_key_auth.md
├── 07_transaction_broadcast/     # 交易广播
│   ├── network_broadcast.md
│   └── mempool_understanding.md
├── 08_complete_workflow/        # 完整流程
│   ├── step_by_step_guide.md
│   └── automated_script.sh
├── 09_troubleshooting/          # 故障排除
│   ├── common_issues.md
│   └── error_solutions.md
└── scripts/                     # 自动化脚本
    ├── setup_environment.sh
    ├── create_wallets.sh
    ├── mine_blocks.sh
    ├── create_transaction.sh
    └── complete_workflow.sh
```

## 快速开始
1. 阅读安装指南（根据您的操作系统选择）
2. 按照环境配置指南设置测试网络
3. 跟随分步指南进行实际操作
4. 使用自动化脚本验证学习成果

## 前置要求
- 基本的命令行操作知识
- 对区块链概念的基本了解
- 足够的磁盘空间（至少10GB用于比特币核心）

## 注意事项
- 本指南使用regtest（回归测试）网络，不会使用真实的比特币
- 所有操作都在本地环境中进行，不会影响主网络
- 建议在虚拟机或隔离环境中进行学习

## 学习路径
1. **基础概念** → 理解区块链和比特币的基本原理
2. **环境搭建** → 安装和配置比特币核心
3. **钱包操作** → 创建钱包和生成地址
4. **挖矿实践** → 理解挖矿和UTXO机制
5. **交易构建** → 手动创建原始交易
6. **交易签名** → 使用私钥签名交易
7. **交易广播** → 将交易发送到网络
8. **完整流程** → 整合所有步骤的完整操作

## 贡献
欢迎提交问题报告和改进建议！

## 许可证
MIT License





