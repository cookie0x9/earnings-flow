"""
Generate mock earnings events and paper-trading logs for demo purposes.
Run: python scripts/generate_demo_data.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import csv
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from earnings_flow.config import PRIMARY_WATCHLIST, STRATEGY_LABELS
from earnings_flow.analysis import SignalDirection, StrategyLabel
from earnings_flow.paper_trading import PaperTradingLogger

np.random.seed(42)


def generate_mock_earnings_events(n_quarters: int = 6) -> pd.DataFrame:
    """Generate realistic mock earnings events for demo."""
    events = []
    base = datetime(2025, 7, 15)  # Q3 2025 start

    earnings_patterns = {
        "TSLA": {"eps_growth": 0.8, "beat_tendency": 0.6, "volatility": 4.0},
        "META": {"eps_growth": 0.9, "beat_tendency": 0.7, "volatility": 3.5},
        "AAPL": {"eps_growth": 0.3, "beat_tendency": 0.5, "volatility": 2.0},
        "NVDA": {"eps_growth": 1.2, "beat_tendency": 0.8, "volatility": 5.0},
        "MSFT": {"eps_growth": 0.5, "beat_tendency": 0.55, "volatility": 2.5},
        "GOOGL": {"eps_growth": 0.4, "beat_tendency": 0.5, "volatility": 2.5},
        "AMZN": {"eps_growth": 0.6, "beat_tendency": 0.55, "volatility": 3.0},
        "QQQ": {"eps_growth": 0.2, "beat_tendency": 0.5, "volatility": 1.5},
        "MSTR": {"eps_growth": 1.5, "beat_tendency": 0.6, "volatility": 6.0},
        "AMD": {"eps_growth": 0.5, "beat_tendency": 0.5, "volatility": 4.5},
    }

    for ticker in PRIMARY_WATCHLIST:
        pattern = earnings_patterns.get(ticker, earnings_patterns["QQQ"])
        eps_base = 0.50 + np.random.random() * 2.0

        for q in range(n_quarters):
            edate = base + timedelta(days=q * 91 + np.random.randint(-7, 7))

            eps_est = round(eps_base * (1 + pattern["eps_growth"] * q / n_quarters), 2)
            surprise = np.random.normal(3, pattern["volatility"])
            eps_actual = round(eps_est * (1 + surprise / 100), 2)

            # Post-earnings returns: beat usually means positive
            ret_1d = round(surprise * 0.4 + np.random.normal(0, 2), 2)
            ret_3d = round(ret_1d + np.random.normal(0, 1.5), 2)
            ret_5d = round(ret_1d + np.random.normal(0, 2.5), 2)

            events.append({
                "ticker": ticker,
                "earnings_date": str(edate.date()),
                "eps_estimate": eps_est,
                "eps_actual": eps_actual,
                "eps_surprise_pct": round(surprise, 1),
                "return_1d": ret_1d,
                "return_3d": ret_3d,
                "return_5d": ret_5d,
            })

    df = pd.DataFrame(events)
    df["earnings_date"] = pd.to_datetime(df["earnings_date"])
    df = df.sort_values(["ticker", "earnings_date"])
    return df


def generate_mock_paper_trades(events: pd.DataFrame) -> list[dict]:
    """Generate realistic paper trades from mock earnings events."""
    trades = []
    trade_id = 1
    balance = 100_000.0

    trading_map = {
        "gap_chase": "LONG",
        "mean_revert": "LONG",
        "fade": "SHORT",
    }

    for _, event in events.iterrows():
        surprise = event.get("eps_surprise_pct", 0) or 0
        ret_1d = event.get("return_1d", 0) or 0

        # Classify
        if surprise > 5:
            strategy = "gap_chase"
        elif ret_1d > 2:
            strategy = "gap_chase"
        elif ret_1d < -2:
            strategy = "mean_revert"
        elif surprise < -5:
            strategy = "fade"
        else:
            continue  # skip watch events

        direction = trading_map[strategy]
        entry_price = round(100 + np.random.random() * 200, 2)
        qty = np.random.randint(5, 30)
        notional = round(entry_price * qty, 2)

        # Portfolio risk check
        if notional > balance * 0.20:
            continue

        balance_before = round(balance, 2)
        balance -= notional

        # Exit after hold period
        if direction == "LONG":
            ret = event.get("return_5d", ret_1d) or 0
        else:
            ret = -(event.get("return_5d", ret_1d) or 0)

        exit_price = round(entry_price * (1 + ret / 100), 2)
        pnl = round((exit_price - entry_price) * qty * (1 if direction == "LONG" else -1), 2)
        pnl_pct = round(ret, 2)

        balance += (notional + pnl)
        balance_after = round(balance, 2)

        entry_ts = pd.Timestamp(event["earnings_date"]) + timedelta(hours=16)
        exit_ts = entry_ts + timedelta(days=5)

        trades.append({
            "trade_id": f"PT-{trade_id:06d}",
            "timestamp": entry_ts.isoformat(),
            "ticker": event["ticker"],
            "direction": direction,
            "price": entry_price,
            "quantity": qty,
            "notional": notional,
            "strategy": strategy,
            "signal_confidence": round(0.6 + np.random.random() * 0.25, 2),
            "entry_rationale": f"财报后策略信号: {strategy}, EPS Surprise {surprise}%",
            "exit_timestamp": exit_ts.isoformat(),
            "exit_price": exit_price,
            "exit_rationale": "持有期满 5 日" if pnl > 0 else "止损/持有期满",
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "balance_before": balance_before,
            "balance_after": balance_after,
        })
        trade_id += 1

    return trades


def main():
    evidence_dir = Path(__file__).resolve().parent.parent / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    print("Generating mock earnings events...")
    events = generate_mock_earnings_events(n_quarters=6)
    events.to_csv(evidence_dir / "mock_earnings_events.csv", index=False)
    print(f"  Saved {len(events)} events to evidence/mock_earnings_events.csv")

    print("Generating mock paper trades...")
    trades = generate_mock_paper_trades(events)

    # Write CSV
    if trades:
        with open(evidence_dir / "paper_trading_log.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
            writer.writeheader()
            writer.writerows(trades)

        # Write JSON
        with open(evidence_dir / "paper_trading_log.json", "w") as f:
            json.dump({
                "account": {"initial_balance": 100000.0, "current_balance": trades[-1]["balance_after"]},
                "trades": trades,
            }, f, indent=2, ensure_ascii=False, default=str)

    print(f"  Saved {len(trades)} trades to evidence/paper_trading_log.csv|json")

    # Print summary
    if trades:
        closed = [t for t in trades if t["pnl"] is not None]
        wins = [t for t in closed if t["pnl"] > 0]
        total_pnl = sum(t["pnl"] for t in closed)
        print(f"\n=== Demo Data Summary ===")
        print(f"Total trades: {len(trades)}")
        print(f"Win rate: {len(wins)/len(closed)*100:.1f}%")
        print(f"Total PnL: ${total_pnl:,.2f}")
        print(f"Final balance: ${trades[-1]['balance_after']:,.2f}")
        print(f"Return: {(trades[-1]['balance_after']/100000 - 1)*100:.2f}%")

    print("\nDone. Run 'streamlit run app.py' to launch the dashboard.")


if __name__ == "__main__":
    main()
