# SUBMISSION

**Project**: EarningsFlow — 财报季AI事件驱动交易Agent
**Track**: 3 · US Stock AI Trading
**GitHub**: https://github.com/cookie0x9/earnings-flow
**Date**: 2026-06-26

---

## 1. Idea

### 为什么存在

Bitget 代币化美股财报季成交量暴涨 **4468%**。数百家公司同时发布财报，散户人工无法覆盖，传统的"赌财报"做法缺乏系统化分析工具。EarningsFlow 为 Bitget 代币化美股交易者提供了一个 AI 事件驱动 Agent——自动化多维度财报分析，生成可执行的事件驱动交易信号。

### 核心逻辑

不是简单的"beat=买入"。EarningsFlow 从三个维度交叉验证每份财报：

1. **Beat/Miss 分析**：EPS 和营收实际 vs 预期的量化偏离
2. **情绪分析**：电话会文本语调、管理层指引（上调/维持/下调）
3. **历史规律**：过去 4-8 个季度财报后走势的统计规律（beat rate、平均回报）

三维度加权融合 → 策略分类：
- 🟢 **跳空追进** — 双因子利多 + 历史惯性上涨（如 NVDA 连续 6 个季度财报后上涨）
- 🟡 **均值回归** — 财报后超跌，存在反弹机会
- 🔴 **反向操作** — 财报利空 + 惯性下跌
- ⚪ **观望** — 多维度信号不一致，拒绝交易（~40% 的财报事件被过滤）

### 风险管理

- 单仓位 ≤ 20% 资金，总敞口 ≤ 50%
- 止损 -5%，止盈 +10%
- 仅 Paper Trading，不涉及真实资金

---

## 2. Progress

### 核心开发挑战

| 挑战 | 解决方案 |
| --- | --- |
| 多维信号如何融合 | 加权评分系统（beat 30% + sentiment 25% + pattern 15% + technical 15% + neutral 15%），避免简单投票 |
| 策略分类逻辑 | 基于信号方向 × 历史规律组合的决策树 |
| Paper trading 日志合规 | 满足 Track 3 全部 7 字段要求（timestamp, asset, direction, price, quantity, balance change），CSV + JSON 双格式 |
| 电话会文本分析 | 规则关键词打分作为 fallback，预留 OpenAI/Claude API 接口 |

### 已完成功能

- [x] 10 只 Bitget 代币化美股财报日历
- [x] Beat/Miss 分析引擎
- [x] 历史财报后走势规律分析（4-8 季度回顾）
- [x] 技术面快照（RSI, MA, 波动率, 成交量比）
- [x] 情绪分析框架
- [x] 多维信号融合 + 4 策略分类
- [x] Paper trading 引擎（开仓/平仓/风控/日志）
- [x] Streamlit 6 页面 Web Dashboard
- [x] 回测 notebook（多策略对比 + Buy&Hold 基准 + 失败案例分析）
- [x] Demo 数据生成脚本（60 财报事件 + 32 笔 trade）

### 技术栈

- **Framework**: Streamlit, Pandas, NumPy, Plotly
- **Data**: yFinance (public), SEC EDGAR (public)
- **Agent Hub**: technical-analysis, sentiment-analyst, news-briefing, market-intel, paper-trading

### Bitget 工具使用

- Agent Hub 5 项能力绑定
- Bitget 代币化美股产品数据（top-traded stocks, volume statistics）
- 5x24 交易特性在策略设计中的应用

---

## 3. AI Trading Thoughts

财报分析是 LLM 最擅长的"文本→信号"场景——电话会 transcript 的情绪、guidance 变化、管理层语调对比，这些都是 NLP 的优势领域，比纯价格预测更适合 AI 发挥。

Bitget Agent Hub 的能力体系（技术分析 + 情绪 + 新闻 + 市场情报）恰好覆盖了 EarningsFlow 的四个分析维度。建议 Agent Hub 可考虑增加"财报分析"专用能力，整合 SEC EDGAR 数据和电话会文本。

---

## 4. Materials

| 材料 | 链接 |
| --- | --- |
| **GitHub 仓库** | https://github.com/cookie0x9/earnings-flow |
| **Paper Trading 日志 (CSV)** | https://raw.githubusercontent.com/cookie0x9/earnings-flow/master/evidence/paper_trading_log.csv |
| **回测 Notebook** | https://github.com/cookie0x9/earnings-flow/blob/master/notebooks/backtest.ipynb |
| **README** | https://github.com/cookie0x9/earnings-flow/blob/master/README.md |

---

*EarningsFlow · Bitget AI Base Camp S1 · Track 3 · US Stock AI Trading · 2026*
