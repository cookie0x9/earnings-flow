"""
EarningsFlow paper trading engine — simulates trade execution,
maintains paper-trading log, and computes performance statistics.

ALL ORDERS ARE PAPER TRADING ONLY. No real funds, no real API keys.
"""

import csv
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from .analysis import EarningsAnalysisReport, StrategyLabel
from .config import (
    MAX_POSITION_SIZE_PCT,
    MAX_PORTFOLIO_RISK_PCT,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
)


@dataclass
class PaperTrade:
    """Single paper-trade record meeting Track 3 evidence field requirements."""
    trade_id: str
    timestamp: str           # ISO 8601
    ticker: str              # asset
    direction: str           # LONG / SHORT
    price: float
    quantity: float
    notional: float          # price * quantity
    strategy: str            # gap_chase / mean_revert / watch / fade
    signal_confidence: float
    entry_rationale: str
    exit_timestamp: Optional[str] = None
    exit_price: Optional[float] = None
    exit_rationale: Optional[str] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    balance_before: Optional[float] = None
    balance_after: Optional[float] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, float) and v is not None:
                d[k] = round(v, 4)
        return d


@dataclass
class PaperTradingAccount:
    """Simulated trading account."""
    initial_balance: float = 100_000.0  # $100k paper money
    balance: float = 100_000.0
    positions: dict = field(default_factory=dict)  # ticker -> {quantity, avg_price, side}
    trade_log: list[PaperTrade] = field(default_factory=list)
    trade_counter: int = 0

    def open_position(
        self,
        ticker: str,
        direction: str,
        price: float,
        quantity: float,
        report: EarningsAnalysisReport,
    ) -> Optional[PaperTrade]:
        """Open a paper-trading position."""
        notional = price * quantity

        # Risk checks
        if notional > self.balance * MAX_POSITION_SIZE_PCT:
            return None  # position size limit
        if notional > self.balance:
            return None  # insufficient balance

        self.trade_counter += 1
        trade = PaperTrade(
            trade_id=f"PT-{self.trade_counter:06d}",
            timestamp=datetime.now().isoformat(),
            ticker=ticker,
            direction=direction,
            price=price,
            quantity=quantity,
            notional=notional,
            strategy=report.strategy.value,
            signal_confidence=report.confidence,
            entry_rationale=report.trade_rationale,
            balance_before=round(self.balance, 2),
        )

        self.positions[ticker] = {
            "quantity": quantity,
            "avg_price": price,
            "direction": direction,
            "trade": trade,
        }
        self.balance -= notional
        trade.balance_after = round(self.balance, 2)
        self.trade_log.append(trade)
        return trade

    def close_position(
        self,
        ticker: str,
        exit_price: float,
        exit_rationale: str = "",
    ) -> Optional[PaperTrade]:
        """Close an existing position and calculate PnL."""
        if ticker not in self.positions:
            return None

        pos = self.positions.pop(ticker)
        trade = pos["trade"]

        if pos["direction"] == "LONG":
            pnl = (exit_price - pos["avg_price"]) * pos["quantity"]
        else:  # SHORT
            pnl = (pos["avg_price"] - exit_price) * pos["quantity"]

        pnl_pct = pnl / (pos["avg_price"] * pos["quantity"]) * 100

        trade.exit_timestamp = datetime.now().isoformat()
        trade.exit_price = exit_price
        trade.exit_rationale = exit_rationale
        trade.pnl = round(pnl, 2)
        trade.pnl_pct = round(pnl_pct, 2)
        trade.balance_before = round(self.balance, 2)
        self.balance += (pos["avg_price"] * pos["quantity"]) + pnl
        trade.balance_after = round(self.balance, 2)

        return trade

    def get_portfolio_value(self, prices: dict[str, float]) -> float:
        """Mark-to-market portfolio value."""
        total = self.balance
        for ticker, pos in self.positions.items():
            if ticker in prices:
                mkt_value = pos["quantity"] * prices[ticker]
                if pos["direction"] == "SHORT":
                    entry_value = pos["quantity"] * pos["avg_price"]
                    total += (entry_value - mkt_value) + entry_value
                else:
                    total += mkt_value
            else:
                total += pos["quantity"] * pos["avg_price"]
        return round(total, 2)


class PaperTradingLogger:
    """Persistent paper-trading log with CSV + JSON export."""

    def __init__(self, log_dir: str = "evidence"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.log_dir / "paper_trading_log.csv"
        self.json_path = self.log_dir / "paper_trading_log.json"
        self.account = PaperTradingAccount()

    def log_trade(self, trade: PaperTrade):
        """Append trade to CSV and JSON logs."""
        self.account.trade_log.append(trade)
        self._save()

    def _save(self):
        """Persist all trades to CSV and JSON."""
        # CSV — use utf-8-sig for Excel compatibility with Chinese characters
        if self.account.trade_log:
            fieldnames = list(self.account.trade_log[0].to_dict().keys())
            with open(self.csv_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for t in self.account.trade_log:
                    writer.writerow(t.to_dict())

        # JSON
        with open(self.json_path, "w") as f:
            json.dump(
                {
                    "account": {
                        "initial_balance": self.account.initial_balance,
                        "current_balance": self.account.balance,
                    },
                    "trades": [t.to_dict() for t in self.account.trade_log],
                },
                f,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

    def load_log(self) -> pd.DataFrame:
        """Load trade log as DataFrame for analysis."""
        if self.csv_path.exists():
            return pd.read_csv(self.csv_path)
        return pd.DataFrame()

    def get_performance_stats(self, prices: dict[str, float] = None) -> dict:
        """Compute performance statistics from trade log."""
        df = self.load_log()
        if df.empty:
            return {"total_trades": 0, "message": "暂无交易记录"}

        closed = df[df["pnl"].notna() & (df["pnl"] != 0)]
        if prices:
            portfolio_value = self.account.get_portfolio_value(prices)
        else:
            portfolio_value = self.account.balance

        stats = {
            "total_trades": len(df),
            "closed_trades": len(closed),
            "open_trades": len(df) - len(closed),
            "win_rate_pct": round(
                len(closed[closed["pnl"] > 0]) / len(closed) * 100, 1
            ) if len(closed) > 0 else 0,
            "total_pnl": round(closed["pnl"].sum(), 2) if len(closed) > 0 else 0,
            "avg_pnl_per_trade": round(closed["pnl"].mean(), 2) if len(closed) > 0 else 0,
            "best_trade": round(closed["pnl"].max(), 2) if len(closed) > 0 else 0,
            "worst_trade": round(closed["pnl"].min(), 2) if len(closed) > 0 else 0,
            "total_return_pct": round(
                (portfolio_value / self.account.initial_balance - 1) * 100, 2
            ),
            "portfolio_value": round(portfolio_value, 2),
            "initial_balance": self.account.initial_balance,
        }

        # Strategy breakdown
        if len(closed) > 0:
            by_strategy = closed.groupby("strategy").agg(
                trades=("pnl", "count"),
                total_pnl=("pnl", "sum"),
                win_rate=("pnl", lambda x: round((x > 0).sum() / len(x) * 100, 1)),
            ).reset_index()
            stats["by_strategy"] = by_strategy.to_dict(orient="records")

        return stats
