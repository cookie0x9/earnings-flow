"""
EarningsFlow earnings pipeline — orchestrates data fetching,
multi-dimensional analysis, and paper-trading signal generation.
"""

from datetime import datetime
from typing import Optional

import pandas as pd

from .data import (
    get_earnings_calendar,
    get_earnings_history,
    get_post_earnings_price_moves,
    get_price_history,
)
from .analysis import (
    EarningsAnalysisReport,
    EarningsBeatAnalysis,
    HistoricalPattern,
    SentimentAnalysis,
    StrategyLabel,
    SignalDirection,
    TechnicalSnapshot,
    analyze_earnings_beat,
    analyze_historical_pattern,
    analyze_sentiment,
    compute_technical_snapshot,
    generate_comprehensive_report,
)


def run_earnings_pipeline(
    tickers: list[str],
    lookback_quarters: int = 4,
    use_mock: bool = False,
) -> list[EarningsAnalysisReport]:
    """
    Full earnings analysis pipeline for a list of tickers.
    Returns one report per ticker with strategy recommendation.
    """
    reports = []

    for t in tickers:
        try:
            # 1. Get earnings calendar
            cal = get_earnings_calendar([t])
            earnings_date = str(datetime.now().date())
            eps_actual = None
            eps_estimate = None
            if not cal.empty:
                row = cal.iloc[0]
                earnings_date = str(row.get("earnings_date", earnings_date))
                eps_actual = row.get("eps_actual", None)
                eps_estimate = row.get("eps_estimate", None)

            # 2. Beat analysis
            beat = analyze_earnings_beat(
                t, earnings_date,
                eps_actual=eps_actual,
                eps_estimate=eps_estimate,
            )

            # 3. Historical pattern
            post_moves = get_post_earnings_price_moves(t, lookback_quarters)
            pattern = analyze_historical_pattern(t, post_moves)

            # 4. Technical snapshot
            price_df = get_price_history(t, period="3mo")
            technical = compute_technical_snapshot(t, price_df)

            # 5. Sentiment (keyword-based as fallback; LLM integration point)
            sentiment = analyze_sentiment(t, earnings_date)

            # 6. Comprehensive report
            report = generate_comprehensive_report(
                t, earnings_date, beat, sentiment, pattern, technical
            )
            reports.append(report)

        except Exception as e:
            # Generate a minimal error report
            report = EarningsAnalysisReport(
                ticker=t,
                earnings_date=str(datetime.now().date()),
                final_signal=SignalDirection.NEUTRAL,
                confidence=0.0,
                strategy=StrategyLabel.WATCH,
                trade_rationale=f"分析异常: {str(e)[:100]}",
                risk_flags=["数据获取失败"],
            )
            from .config import SAFETY_NOTICE
            report.safety_notice = SAFETY_NOTICE
            reports.append(report)

    return reports


def run_single_ticker_pipeline(
    ticker: str,
    eps_actual: Optional[float] = None,
    eps_estimate: Optional[float] = None,
    revenue_actual: Optional[float] = None,
    revenue_estimate: Optional[float] = None,
    transcript_text: str = "",
    guidance_text: str = "",
    lookback_quarters: int = 4,
) -> EarningsAnalysisReport:
    """Run pipeline for a single ticker with optional user-provided data."""
    earnings_date = str(datetime.now().date())

    beat = analyze_earnings_beat(
        ticker, earnings_date,
        eps_actual=eps_actual,
        eps_estimate=eps_estimate,
        revenue_actual=revenue_actual,
        revenue_estimate=revenue_estimate,
    )

    sentiment = analyze_sentiment(
        ticker, earnings_date,
        transcript_text=transcript_text,
        guidance_text=guidance_text,
    )

    post_moves = get_post_earnings_price_moves(ticker, lookback_quarters)
    pattern = analyze_historical_pattern(ticker, post_moves)

    price_df = get_price_history(ticker, period="3mo")
    technical = compute_technical_snapshot(ticker, price_df)

    return generate_comprehensive_report(ticker, earnings_date, beat, sentiment, pattern, technical)
