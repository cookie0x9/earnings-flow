# EVIDENCE_INDEX

**Project**: EarningsFlow | **Generated**: 2026-06-25

## Evidence Inventory

| Evidence | Type | Command / Source | Path | Public Link | Verified At |
| --- | --- | --- | --- | --- | --- |
| Paper trading log (CSV) | required | `python scripts/generate_demo_data.py` | evidence/paper_trading_log.csv | — (Stage 4) | 2026-06-25 |
| Paper trading log (JSON) | required | `python scripts/generate_demo_data.py` | evidence/paper_trading_log.json | — (Stage 4) | 2026-06-25 |
| Mock earnings events | supplementary | `python scripts/generate_demo_data.py` | evidence/mock_earnings_events.csv | — (Stage 4) | 2026-06-25 |
| Backtest notebook | optional (code incl.) | `jupyter notebook notebooks/backtest.ipynb` | notebooks/backtest.ipynb | — (Stage 4) | 2026-06-25 |
| Streamlit Dashboard | required (demo) | `streamlit run app.py` | app.py | http://localhost:8501 | 2026-06-25 |
| README | required | — | README.md | — (Stage 4) | 2026-06-25 |
| Requirements file | required (reproducibility) | `pip install -r requirements.txt` | requirements.txt | — (Stage 4) | 2026-06-25 |
| Source code | required | — | earnings_flow/ | — (Stage 4) | 2026-06-25 |

## Evidence Ladder

| Level | Evidence | Status |
| --- | --- | --- |
| **Local reproducible** | `generate_demo_data.py` regenerates all logs | ✅ verified |
| **Local reproducible** | Backtest notebook runs with code included | ✅ structure complete; needs `jupyter execute` verification |
| **Local reproducible** | Streamlit dashboard runs on localhost:8501 | ✅ verified |
| **Reproducible by others** | README with install + run instructions | ✅ |
| **Reproducible by others** | requirements.txt with pinned deps | ✅ (unpinned for compatibility) |
| **Public** | GitHub repo (pending Stage 4) | ⏳ Stage 4 |
| **Public** | Dashboard deploy (optional, pending Stage 4) | ⏳ Stage 4 |
| **Usage / Integration** | Paper trading log as CSV (machine-readable) | ✅ |
| **Usage / Integration** | Agent Hub capability declarations | ✅ config.py |

## Gaps Before Submission

| Gap | Severity | Action |
| --- | --- | --- |
| GitHub repo not yet public | blocking (Stage 4) | `gh repo create --public` in Stage 4 |
| Paper trading log uses mock data | medium | Run with real yFinance data for final submission run |
| Backtest notebook not verified with real data | medium | Execute against real yFinance earnings data |
| No demo video (dashboard has no login, so optional) | low | Record 2-3 min walkthrough for submission strength |
| Agent Hub capabilities declared but not Stage 3 resolved | low | Run `resolve_resource_binding.py` if any capability is used in code |
