"""
EarningsFlow data layer — fetches earnings calendar, historical prices,
financial data via yFinance public API.
"""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

from .config import PRIMARY_WATCHLIST, DATA_SOURCES


def get_earnings_calendar(tickers: Optional[list[str]] = None) -> pd.DataFrame:
    """
    Fetch upcoming and recent earnings dates for tracked stocks.
    Uses yFinance .calendar and .earnings_dates where available.
    Returns DataFrame with ticker, earnings_date, eps_estimate, revenue_estimate.
    """
    tickers = tickers or PRIMARY_WATCHLIST
    rows = []

    for t in tickers:
        try:
            stock = yf.Ticker(t)
            cal = stock.calendar
            if cal is not None and isinstance(cal, dict):
                earnings_date = cal.get("Earnings Date", None)
                if earnings_date is not None:
                    if isinstance(earnings_date, (list, tuple)):
                        earnings_date = earnings_date[0]
                    rows.append({
                        "ticker": t,
                        "earnings_date": pd.Timestamp(earnings_date),
                        "eps_estimate": cal.get("Earnings Estimate", None),
                        "revenue_estimate": cal.get("Revenue Estimate", None),
                        "eps_actual": cal.get("Earnings Estimate", None),  # placeholder
                    })
        except Exception:
            continue

    if not rows:
        return pd.DataFrame(columns=["ticker", "earnings_date", "eps_estimate", "revenue_estimate", "eps_actual"])

    df = pd.DataFrame(rows)
    df["earnings_date"] = pd.to_datetime(df["earnings_date"])
    return df.sort_values("earnings_date")


def get_price_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """Fetch OHLCV price history for a ticker."""
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    if df.empty:
        return df
    df.index = pd.to_datetime(df.index)
    return df


def get_earnings_history(ticker: str) -> pd.DataFrame:
    """Fetch historical quarterly earnings (EPS actual vs estimate)."""
    stock = yf.Ticker(ticker)
    try:
        earnings = stock.earnings_dates
        if earnings is not None and not earnings.empty:
            df = earnings.reset_index()
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            return df.sort_values("earnings_date", ascending=False) if "earnings_date" in df.columns else df
    except Exception:
        pass
    return pd.DataFrame()


def get_post_earnings_price_moves(
    ticker: str, lookback_quarters: int = 4
) -> list[dict]:
    """
    For each historical earnings date, compute the 1-day, 3-day, and 5-day
    post-announcement price change (close-to-close).
    """
    earnings_df = get_earnings_history(ticker)
    if earnings_df.empty:
        return []

    price = get_price_history(ticker, period="2y")
    if price.empty:
        return []

    results = []
    for _, row in earnings_df.head(lookback_quarters).iterrows():
        edate = pd.Timestamp(row.get("earnings_date") or row.get("earnings_date"))
        if pd.isna(edate):
            continue

        # Find nearest trading day in price data
        nearby = price.index[price.index >= edate]
        if len(nearby) == 0:
            continue
        idx = price.index.get_loc(nearby[0])
        pre_close = float(price["Close"].iloc[max(0, idx - 1)])

        moves = {}
        for label, offset in [("1d", 1), ("3d", 3), ("5d", 5)]:
            if idx + offset < len(price):
                moves[f"return_{label}"] = round(
                    (float(price["Close"].iloc[idx + offset]) / float(price["Close"].iloc[idx]) - 1) * 100, 2
                )

        results.append({
            "ticker": ticker,
            "earnings_date": str(edate.date()),
            "eps_surprise_pct": row.get("eps_actual", None),
            "pre_close": round(pre_close, 2),
            **moves,
        })

    return results


def get_beat_rate(ticker: str, quarters: int = 8) -> dict:
    """Calculate historical EPS beat rate and average surprise."""
    moves = get_post_earnings_price_moves(ticker, lookback_quarters=quarters)
    if not moves:
        return {"ticker": ticker, "beat_rate_pct": None, "quarters_analyzed": 0, "avg_return_1d": None}

    positive_moves = [m for m in moves if m.get("return_1d", 0) > 0]
    returns_1d = [m["return_1d"] for m in moves if m.get("return_1d") is not None]

    return {
        "ticker": ticker,
        "quarters_analyzed": len(moves),
        "positive_rate_pct": round(len(positive_moves) / len(moves) * 100, 1) if moves else None,
        "avg_return_1d": round(sum(returns_1d) / len(returns_1d), 2) if returns_1d else None,
        "avg_return_3d": round(sum(m.get("return_3d", 0) or 0 for m in moves) / len(moves), 2),
        "avg_return_5d": round(sum(m.get("return_5d", 0) or 0 for m in moves) / len(moves), 2),
    }
