# EarningsFlow — 财报季AI事件驱动交易Agent

**Bitget AI Base Camp Season 1 · Track 3 · US Stock AI Trading**

EarningsFlow 是专为 Bitget 代币化美股财报季设计的 AI 事件驱动 Agent。Bitget 财报季代币化美股期货成交量暴涨 **4468%**——EarningsFlow 通过多维度财报分析（Beat/Miss、电话会情绪、历史规律对比、技术面）生成可执行的交易信号。

> ⚠️ **免责声明**: 本系统仅供研究和教育用途，所有交易信号均为 paper trading（模拟盘），不构成投资建议。

---

## 核心机制

```
📅 财报日历监控 → 🔔 财报发布
  ├─ 📊 实际 vs 预期 (EPS/Revenue beat or miss)
  ├─ 🗣️ 电话会文本分析 (情绪、guidance、关键指标)
  └─ 📈 历史规律对比 (本次 vs 过去 4-8 季度走势)
       ↓
🤖 AI 策略生成 → 信号分类:
  🟢 跳空追进 (Gap Chase)  — 双因子利多 + 历史惯性上涨
  🟡 均值回归 (Mean Revert) — 财报后超跌反弹
  🔴 反向操作 (Fade)        — 财报利空 + 惯性下跌
  ⚪ 观望 (Watch)            — 多维度信号不一致
       ↓
📝 Paper Trading 执行 → 📊 绩效统计
```

## 目录结构

```
earnings-flow/
├── app.py                          # Streamlit Web Dashboard
├── requirements.txt                # Python dependencies
├── README.md
├── earnings_flow/
│   ├── __init__.py
│   ├── config.py                   # Configuration & Bitget watchlist
│   ├── data.py                     # Data fetching (yFinance, SEC EDGAR)
│   ├── analysis.py                 # Multi-dimensional earnings analysis
│   ├── pipeline.py                 # Orchestration pipeline
│   └── paper_trading.py            # Paper trading engine & logger
├── notebooks/
│   └── backtest.ipynb              # Multi-strategy backtest notebook
├── scripts/
│   └── generate_demo_data.py       # Demo data generator
└── evidence/
    ├── paper_trading_log.csv       # Paper trading log (Track 3 required)
    ├── paper_trading_log.json
    └── mock_earnings_events.csv    # Mock earnings data
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 生成 Demo 数据

```bash
python scripts/generate_demo_data.py
```

### 3. 启动 Dashboard

```bash
streamlit run app.py
```

Dashboard 将在 `http://localhost:8501` 启动。

### 4. 运行回测 Notebook

```bash
jupyter notebook notebooks/backtest.ipynb
```

## Web Dashboard 功能

| 页面 | 功能 |
| --- | --- |
| 📅 **财报日历** | Bitget 代币化美股财报日历、预期 vs 实际数据 |
| 🔬 **个股深度分析** | 四维度分析（Beat/Miss + 情绪 + 历史规律 + 技术面）→ 策略建议 |
| 📈 **策略信号面板** | 多标的信号总览、一键 Paper Trading 执行 |
| 📋 **交易日志** | 完整 Paper Trading 日志（含 Track 3 全部必填字段） |
| 📊 **绩效统计** | 策略胜率/回报/MDD/Sharpe、按策略分解图表 |

## Bitget 代币化美股覆盖

| 标的 | Bitget 累计成交量 | 备注 |
| --- | --- | --- |
| TSLA (Tesla) | $6.3B+ | 最高成交量 |
| META (Meta) | $2.05B (财报季) | 财报季暴涨 |
| AAPL (Apple) | $1.03B | 稳定标的 |
| NVDA (Nvidia) | 高速增长 | AI 概念 |
| MSFT / GOOGL / AMZN | 高活跃度 | 科技龙头 |
| QQQ (Nasdaq-100 ETF) | $460M | ETF 覆盖 |
| MSTR (MicroStrategy) | $1.43B | 高波动 |
| AMD | 中等活跃 | 半导体 |

## Agent Hub 能力绑定

| 能力 ID | 用途 | 状态 |
| --- | --- | --- |
| `technical-analysis` | OHLCV 指标计算 (RSI, MA, 波动率) | declared |
| `sentiment-analyst` | 电话会语调和情绪分析 | declared |
| `news-briefing` | 财报新闻溯源 | declared |
| `market-intel` | 机构评级变化分析 | declared |
| `paper-trading` | 模拟盘交易流程 | declared |

## Paper Trading 日志格式 (Track 3 要求)

每条交易记录包含:

- `timestamp` — ISO 8601 时间戳
- `ticker` — 资产标识
- `direction` — LONG / SHORT
- `price` — 成交价格
- `quantity` — 数量
- `notional` — 名义价值
- `balance_before` / `balance_after` — 账户余额变化
- `pnl` / `pnl_pct` — 盈亏

## 安全边界

- ✅ 仅 Paper Trading，不涉及真实资金
- ✅ 不存储 API Key、密码、私钥或 UID
- ✅ 所有数据来自公开源 (yFinance, SEC EDGAR)
- ✅ 分析报告标注"不构成投资建议"
- ✅ 未声称 Agent Hub 提供美股数据

## 技术栈

- **Dashboard**: Streamlit + Plotly
- **数据**: yFinance, SEC EDGAR (public)
- **分析**: NumPy, Pandas
- **回测**: Jupyter Notebook
- **Agent 框架**: Bitget Agent Hub (capability binding, Stage 3)

---

*Bitget AI Base Camp S1 · Track 3 · US Stock AI Trading · 2026*
