# DEPLOYMENT PLAN

**Project**: EarningsFlow | **Date**: 2026-06-25 | **Status**: Pending Approval

## Selected Public Surfaces

| Surface | Why | Required by Track |
| --- | --- | --- |
| **Public GitHub repository** | Required by Track 3; primary public artifact | Required |
| **Optional Streamlit Cloud deploy** | Makes dashboard accessible without local install | Optional (bonus) |

Fallback: GitHub-only is valid for Track 3. If Streamlit Cloud deploy fails, GitHub repo alone satisfies minimum.

## Expected Public URLs

| URL | Type | Status |
| --- | --- | --- |
| `https://github.com/<user>/earnings-flow` | Public repo | Pending creation |
| (Optional) `https://<app>.streamlit.app` | Web demo | Pending user decision |

## Track & Submission Route

- **Track**: 3 · US Stock AI Trading
- **Route**: Standard Track 3 (not Open Innovation)

## Track-Specific Public Material Requirements

| Requirement | How Met |
| --- | --- |
| Public GitHub repo or Demo link | GitHub public repo |
| Paper trading log (public) | `evidence/paper_trading_log.csv` in repo |
| README with install/run instructions | README.md already written |
| Project description | SUBMISSION.md (to be written after public links verified) |
| Optional: Backtest notebook | `notebooks/backtest.ipynb` in repo |
| Optional: Demo video | Not required (dashboard no login needed), but recommended |

## Public Repository

| Field | Value |
| --- | --- |
| **Name** | `earnings-flow` |
| **Owner** | `<from gh api user>` |
| **Visibility** | Public |
| **Branch** | `main` |
| **Description** | EarningsFlow — 财报季AI事件驱动交易Agent | Bitget AI Base Camp S1 · Track 3 |

## Optional Web Demo

| Field | Value |
| --- | --- |
| **Provider** | Streamlit Cloud (free tier) |
| **Runtime** | Python 3.10+ |
| **Build** | `pip install -r requirements.txt` |
| **Start** | `streamlit run app.py` |
| **Env vars** | None required (public data only) |

## Verification Method

- Open GitHub repo URL in incognito browser → verify README visible
- Open `evidence/paper_trading_log.csv` raw URL → verify accessible
- Open `notebooks/backtest.ipynb` → verify renders on GitHub
- If Streamlit Cloud: open app URL → verify dashboard loads without login

## Known Blockers

- `gh` CLI must be installed and functional
- GitHub account must be authorized (device-code handoff)
- Streamlit Cloud deploy requires GitHub connection (optional, pause for user)

## Rollback / No-Deploy Fallback

- If `gh` is unavailable: manual GitHub repo creation via web → paste URL into records
- If push fails: record the failure in DEPLOYMENT_RECORD.md as blocking
- GitHub-only is sufficient; Streamlit Cloud is bonus

## Operations Requiring User Pause

- `gh auth login` device-code handoff
- Streamlit Cloud OAuth / account selection (if chosen)
- Final competition-form submission
