# TRACK_CHECKLIST

**Project**: EarningsFlow | **Track**: 3 · US Stock AI Trading | **Reviewed**: 2026-06-25

## Track 3 Required Materials

| Material | Required | Status | Evidence Path | Public Link | Risk Note |
| --- | --- | --- | --- | --- | --- |
| Project description | required | satisfied | submission/PROJECT_DESCRIPTION_REVIEW.md | — (Stage 4) | Section 1/2 drafts ready, needs final polish |
| GitHub repo or Demo link | required | satisfied | github-earnings-flow/ | — (Stage 4) | Public repo creation pending Stage 4 |
| Live trading record or paper trading log | required | satisfied | evidence/paper_trading_log.csv, evidence/paper_trading_log.json | — (Stage 4) | 32 paper trades, all required fields present (timestamp, asset, direction, price, quantity, balance change). Demo data only; needs real yFinance data run before submission. |

## Track 3 Optional / Supplementary

| Material | Required | Status | Evidence Path | Public Link | Risk Note |
| --- | --- | --- | --- | --- | --- |
| Backtest report (code/notebook) | optional | satisfied | notebooks/backtest.ipynb | — (Stage 4) | Multi-strategy backtest with comparison charts; code included |
| Demo video | optional (required if login needed) | not_yet_required | — | — | Dashboard is public (no login), so video is optional. Recommended for submission strength. |

## Required Field Verification (Paper Trading Log)

| Field | Present | Example |
| --- | --- | --- |
| timestamp | ✅ | 2026-04-18T16:00:00 |
| asset (ticker) | ✅ | AAPL, AMD, TSLA, etc. |
| direction | ✅ | LONG / SHORT |
| price | ✅ | 118.36 |
| quantity | ✅ | 19 |
| account balance change | ✅ | balance_before: 100000.0 → balance_after: 100051.11 |

## Bitget Connection

| Item | Status |
| --- | --- |
| Bitget tokenized stock coverage | ✅ 10 stocks from Bitget top-traded list (TSLA $6.3B+, META $2.05B, AAPL $1.03B, NVDA, MSFT, GOOGL, AMZN, QQQ $460M, MSTR $1.43B, AMD) |
| Bitget 4468% earnings season volume data point | ✅ Referenced in thesis and Project Description |
| Agent Hub capability binding | ✅ 5 capabilities declared (technical-analysis, sentiment-analyst, news-briefing, market-intel, paper-trading) |
| 5x24 trading characteristic | ✅ Referenced in strategy rationale |

## Safety Checks

| Check | Status |
| --- | --- |
| Paper trading only (no real funds) | ✅ |
| No API keys / secrets / UID stored | ✅ |
| Safety notice on all outputs | ✅ |
| Data sources disclosed as public | ✅ |
| No claim Agent Hub provides US-stock data | ✅ |

## Local MVP Acceptance

**Conclusion**: `local-mvp-accepted`

All required materials present and reproducible:
- Paper trading log with all 7 required fields
- Backtest notebook with runnable code
- Streamlit dashboard runs locally
- `python scripts/generate_demo_data.py` regenerates all evidence
- `streamlit run app.py` launches interactive dashboard
