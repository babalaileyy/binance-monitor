# Binance Monitor

一个用于监控币安（Binance）特定加密货币价格并发送邮件通知的 Python 项目。

## 项目结构

本项目采用现代化的 `src` 布局：

```text
binance-monitor/
├── src/
│   └── binance_monitor/    # 源代码目录
│       ├── api/            # 币安 API 交互模块
│       ├── core/           # 核心监控逻辑
│       ├── notification/   # 邮件通知模块
│       ├── config/         # 配置管理模块
│       └── utils/          # 通用工具
├── tests/                  # 测试代码
├── config/                 # 配置文件 (不要提交敏感信息)
├── pyproject.toml          # 项目依赖和配置
└── README.md               # 项目文档
```

## 快速开始

### 1. 环境要求

- Python 3.10+

### 2. 安装依赖

```bash
pip install -e .
```

或者直接安装依赖：

```bash
pip install ccxt pydantic pydantic-settings schedule loguru python-dotenv
```

### 3. 配置

复制 `config/config.yaml.example` 为 `config/config.yaml` 并填入你的配置信息（邮箱 SMTP 设置等）。

### 4. 运行

```bash
python -m binance_monitor.main
```
