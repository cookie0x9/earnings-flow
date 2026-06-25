"""
EarningsFlow config — Bitget tokenized US stocks watchlist,
earnings calendar defaults, and Agent Hub capability mapping.
"""

# Bitget tokenized US stocks (verified: TSLA, META, AAPL, NVDA are top-traded)
# Full list from Bitget tokenized equity offerings via Ondo + XStocks
BITGET_TOKENIZED_STOCKS = [
    "TSLA",   # Tesla — cumulative $6.3B+ volume on Bitget
    "META",   # Meta — $2.05B during earnings season
    "AAPL",   # Apple — $1.03B cumulative
    "NVDA",   # Nvidia — fastest growing spot volume
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet
    "AMZN",   # Amazon
    "QQQ",    # Nasdaq-100 ETF — $460M cumulative
    "MSTR",   # MicroStrategy — $1.43B cumulative
    "AMD",    # AMD
    "NFLX",   # Netflix
    "COIN",   # Coinbase — crypto adjacency
]

# Primary focus: highest Bitget volume + clear earnings patterns
PRIMARY_WATCHLIST = ["TSLA", "META", "AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "QQQ", "MSTR", "AMD"]

# Strategy classification labels
STRATEGY_LABELS = {
    "gap_chase": "跳空追进",
    "mean_revert": "均值回归",
    "watch": "观望",
    "fade": "反向操作",
}

# Risk parameters (paper-trading only)
MAX_POSITION_SIZE_PCT = 0.20   # max 20% of portfolio per position
MAX_PORTFOLIO_RISK_PCT = 0.50  # max 50% total exposure
STOP_LOSS_PCT = -0.05           # stop loss at -5%
TAKE_PROFIT_PCT = 0.10         # take profit at +10%

# Data sources (all public)
DATA_SOURCES = {
    "prices": "yFinance (public)",
    "earnings_calendar": "yFinance (public)",
    "sec_filings": "SEC EDGAR (public)",
    "transcripts": "SEC EDGAR / Fool Earnings (public)",
}

# Agent Hub capability mapping (declared, not yet resolved via Stage 3 binding)
AGENT_HUB_CAPABILITIES = {
    "technical-analysis": {"purpose": "OHLCV指标计算", "status": "declared"},
    "sentiment-analyst": {"purpose": "电话会语调分析", "status": "declared"},
    "news-briefing": {"purpose": "财报新闻溯源", "status": "declared"},
    "market-intel": {"purpose": "机构评级变化分析", "status": "declared"},
    "paper-trading": {"purpose": "模拟盘交易流程", "status": "declared"},
}

# Safety notice — displayed in all generated outputs
SAFETY_NOTICE = (
    "⚠️ 免责声明：本系统仅供研究和教育用途，所有交易信号均为模拟盘 (paper-trading)，"
    "不构成投资建议。历史回测表现不代表未来收益。"
)
