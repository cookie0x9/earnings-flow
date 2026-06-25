"""
EarningsFlow analysis engine — multi-dimensional earnings analysis:
1. Actual vs Estimate (beat / miss)
2. Earnings call sentiment & guidance
3. Historical post-earnings pattern comparison
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import pandas as pd


class SignalDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class StrategyLabel(str, Enum):
    GAP_CHASE = "gap_chase"        # 跳空追进
    MEAN_REVERT = "mean_revert"    # 均值回归
    WATCH = "watch"                 # 观望
    FADE = "fade"                   # 反向操作


@dataclass
class EarningsBeatAnalysis:
    """Analysis of EPS/Revenue beat or miss."""
    ticker: str
    earnings_date: str
    eps_actual: Optional[float] = None
    eps_estimate: Optional[float] = None
    eps_surprise_pct: Optional[float] = None
    revenue_actual: Optional[float] = None
    revenue_estimate: Optional[float] = None
    revenue_surprise_pct: Optional[float] = None
    signal: SignalDirection = SignalDirection.NEUTRAL
    summary: str = ""


@dataclass
class SentimentAnalysis:
    """Earnings call transcript sentiment analysis."""
    ticker: str
    earnings_date: str
    overall_sentiment: SignalDirection = SignalDirection.NEUTRAL
    sentiment_score: float = 0.0  # -1.0 to 1.0
    guidance_signal: SignalDirection = SignalDirection.NEUTRAL
    guidance_detail: str = ""
    key_positives: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list)
    management_tone: str = ""
    summary: str = ""


@dataclass
class HistoricalPattern:
    """Post-earnings price pattern from prior quarters."""
    ticker: str
    quarters_analyzed: int = 0
    beat_rate_pct: Optional[float] = None
    avg_return_1d: Optional[float] = None
    avg_return_3d: Optional[float] = None
    avg_return_5d: Optional[float] = None
    recent_moves: list[dict] = field(default_factory=list)
    pattern_label: str = ""  # e.g. "惯涨" / "惯跌" / "无规律"
    summary: str = ""


@dataclass
class TechnicalSnapshot:
    """Pre-earnings technical posture."""
    ticker: str
    rsi_14: Optional[float] = None
    ma_20: Optional[float] = None
    ma_50: Optional[float] = None
    close: Optional[float] = None
    volatility_30d: Optional[float] = None
    volume_vs_avg: Optional[float] = None  # ratio
    signal: SignalDirection = SignalDirection.NEUTRAL
    summary: str = ""


@dataclass
class EarningsAnalysisReport:
    """Complete multi-dimensional earnings analysis."""
    ticker: str
    earnings_date: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    beat_analysis: Optional[EarningsBeatAnalysis] = None
    sentiment_analysis: Optional[SentimentAnalysis] = None
    historical_pattern: Optional[HistoricalPattern] = None
    technical_snapshot: Optional[TechnicalSnapshot] = None

    final_signal: SignalDirection = SignalDirection.NEUTRAL
    confidence: float = 0.0  # 0.0 to 1.0
    strategy: StrategyLabel = StrategyLabel.WATCH
    trade_rationale: str = ""

    risk_flags: list[str] = field(default_factory=list)
    safety_notice: str = ""

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "earnings_date": self.earnings_date,
            "generated_at": self.generated_at,
            "final_signal": self.final_signal.value,
            "confidence": self.confidence,
            "strategy": self.strategy.value,
            "strategy_label": {
                "gap_chase": "跳空追进",
                "mean_revert": "均值回归",
                "watch": "观望",
                "fade": "反向操作",
            }.get(self.strategy.value, self.strategy.value),
            "trade_rationale": self.trade_rationale,
            "beat_summary": self.beat_analysis.summary if self.beat_analysis else "",
            "sentiment_summary": self.sentiment_analysis.summary if self.sentiment_analysis else "",
            "pattern_summary": self.historical_pattern.summary if self.historical_pattern else "",
            "technical_summary": self.technical_snapshot.summary if self.technical_snapshot else "",
            "risk_flags": self.risk_flags,
            "safety_notice": self.safety_notice,
        }


def analyze_earnings_beat(
    ticker: str,
    earnings_date: str,
    eps_actual: Optional[float] = None,
    eps_estimate: Optional[float] = None,
    revenue_actual: Optional[float] = None,
    revenue_estimate: Optional[float] = None,
) -> EarningsBeatAnalysis:
    """Analyze EPS and revenue beat/miss vs consensus."""
    analysis = EarningsBeatAnalysis(ticker=ticker, earnings_date=earnings_date)

    if eps_actual is not None and eps_estimate is not None and eps_estimate != 0:
        analysis.eps_actual = eps_actual
        analysis.eps_estimate = eps_estimate
        analysis.eps_surprise_pct = round((eps_actual / eps_estimate - 1) * 100, 2)

    if revenue_actual is not None and revenue_estimate is not None and revenue_estimate != 0:
        analysis.revenue_actual = revenue_actual
        analysis.revenue_estimate = revenue_estimate
        analysis.revenue_surprise_pct = round((revenue_actual / revenue_estimate - 1) * 100, 2)

    # Determine signal
    eps_surp = analysis.eps_surprise_pct
    rev_surp = analysis.revenue_surprise_pct

    if eps_surp is not None and eps_surp > 5.0:
        if rev_surp is not None and rev_surp > 0:
            analysis.signal = SignalDirection.BULLISH
            analysis.summary = f"双重超预期：EPS +{eps_surp}%，营收 +{rev_surp}%"
        else:
            analysis.signal = SignalDirection.NEUTRAL
            analysis.summary = f"EPS超预期 +{eps_surp}%，但营收不及预期"
    elif eps_surp is not None and eps_surp < -5.0:
        analysis.signal = SignalDirection.BEARISH
        analysis.summary = f"EPS大幅不及预期 {eps_surp}%"
    elif eps_surp is not None and -5.0 <= eps_surp <= 5.0:
        analysis.signal = SignalDirection.NEUTRAL
        analysis.summary = f"EPS基本符合预期，偏差 {eps_surp}%"
    else:
        analysis.summary = "财报数据待确认"

    return analysis


def analyze_sentiment(
    ticker: str,
    earnings_date: str,
    transcript_text: str = "",
    guidance_text: str = "",
) -> SentimentAnalysis:
    """
    Analyze earnings call sentiment.
    In production, this would use an LLM. Here we provide a rules-based
    scoring framework that can be enhanced with OpenAI / Claude.
    """
    analysis = SentimentAnalysis(ticker=ticker, earnings_date=earnings_date)

    # Rule-based keyword scoring as fallback (LLM integration point)
    positive_words = [
        "strong", "growth", "record", "beat", "raise", "outperform",
        "accelerating", "momentum", "robust", "expansion", "improved",
        "confident", "upgrade", "positive outlook", "increased demand",
    ]
    negative_words = [
        "decline", "weak", "headwind", "miss", "lower", "slowdown",
        "challenging", "pressure", "cautious", "downgrade", "uncertainty",
        "softening", "supply chain", "inflationary", "recession",
    ]

    text_lower = (transcript_text + " " + guidance_text).lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    total = pos_count + neg_count
    if total > 0:
        analysis.sentiment_score = round((pos_count - neg_count) / total, 2)
    else:
        analysis.sentiment_score = 0.0

    if analysis.sentiment_score > 0.2:
        analysis.overall_sentiment = SignalDirection.BULLISH
    elif analysis.sentiment_score < -0.2:
        analysis.overall_sentiment = SignalDirection.BEARISH
    else:
        analysis.overall_sentiment = SignalDirection.NEUTRAL

    # Guidance signal
    guidance_keywords = {
        "raise": SignalDirection.BULLISH,
        "reaffirm": SignalDirection.NEUTRAL,
        "lower": SignalDirection.BEARISH,
        "cut": SignalDirection.BEARISH,
    }
    guidance_lower = guidance_text.lower()
    for kw, direction in guidance_keywords.items():
        if kw in guidance_lower:
            analysis.guidance_signal = direction
            analysis.guidance_detail = f"管理层指引中包含关键词'{kw}'"
            break

    if not guidance_text:
        analysis.guidance_detail = "暂无电话会文本数据"

    if pos_count > 0:
        analysis.key_positives = [w for w in positive_words if w in text_lower][:3]
    if neg_count > 0:
        analysis.key_risks = [w for w in negative_words if w in text_lower][:3]

    analysis.summary = (
        f"情绪评分 {analysis.sentiment_score:.2f}，"
        f"整体{'偏多' if analysis.overall_sentiment == SignalDirection.BULLISH else '偏空' if analysis.overall_sentiment == SignalDirection.BEARISH else '中性'}"
    )

    return analysis


def analyze_historical_pattern(ticker: str, post_moves: list[dict]) -> HistoricalPattern:
    """Analyze historical post-earnings price behavior."""
    pattern = HistoricalPattern(ticker=ticker)

    if not post_moves:
        pattern.summary = "历史数据不足，无法判断规律"
        return pattern

    pattern.quarters_analyzed = len(post_moves)
    pattern.recent_moves = post_moves

    returns_1d = [m.get("return_1d", 0) or 0 for m in post_moves]
    returns_3d = [m.get("return_3d", 0) or 0 for m in post_moves]
    returns_5d = [m.get("return_5d", 0) or 0 for m in post_moves]

    pattern.avg_return_1d = round(sum(returns_1d) / len(returns_1d), 2)
    pattern.avg_return_3d = round(sum(returns_3d) / len(returns_3d), 2)
    pattern.avg_return_5d = round(sum(returns_5d) / len(returns_5d), 2)

    positive_rate = sum(1 for r in returns_1d if r > 0) / len(returns_1d)
    pattern.beat_rate_pct = round(positive_rate * 100, 1)

    if positive_rate >= 0.75:
        pattern.pattern_label = "惯涨"
        pattern.summary = f"过去 {len(post_moves)} 次财报中 {pattern.beat_rate_pct}% 次日上涨，平均 +{pattern.avg_return_1d}%，呈财报后上涨惯性"
    elif positive_rate <= 0.25:
        pattern.pattern_label = "惯跌"
        pattern.summary = f"过去 {len(post_moves)} 次财报中仅 {pattern.beat_rate_pct}% 次日上涨，平均 {pattern.avg_return_1d}%，呈财报后下跌惯性"
    else:
        pattern.pattern_label = "无规律"
        pattern.summary = f"过去 {len(post_moves)} 次财报次日涨跌各半，无明显方向性规律"

    return pattern


def compute_technical_snapshot(
    ticker: str, price_df: pd.DataFrame
) -> TechnicalSnapshot:
    """Compute pre-earnings technical indicators."""
    import numpy as np

    snap = TechnicalSnapshot(ticker=ticker)

    if price_df.empty or len(price_df) < 50:
        snap.summary = "价格数据不足，无法计算技术指标"
        return snap

    closes = price_df["Close"]
    snap.close = float(closes.iloc[-1])

    # RSI-14
    delta = closes.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    snap.rsi_14 = round(float(100 - (100 / (1 + rs.iloc[-1]))), 1) if not pd.isna(rs.iloc[-1]) else None

    # Moving averages
    snap.ma_20 = round(float(closes.rolling(20).mean().iloc[-1]), 2)
    snap.ma_50 = round(float(closes.rolling(50).mean().iloc[-1]), 2) if len(closes) >= 50 else None

    # 30-day volatility (annualized)
    daily_returns = closes.pct_change().dropna()
    snap.volatility_30d = round(float(daily_returns.tail(30).std() * np.sqrt(252) * 100), 1)

    # Volume ratio
    if "Volume" in price_df.columns and len(price_df) >= 50:
        avg_vol = float(price_df["Volume"].tail(50).mean())
        last_vol = float(price_df["Volume"].iloc[-1])
        snap.volume_vs_avg = round(last_vol / avg_vol, 2) if avg_vol > 0 else None

    # Signal
    if snap.rsi_14 and snap.rsi_14 > 70:
        snap.signal = SignalDirection.BEARISH  # overbought
        snap.summary = f"RSI={snap.rsi_14} 超买区，短期回调风险"
    elif snap.rsi_14 and snap.rsi_14 < 30:
        snap.signal = SignalDirection.BULLISH  # oversold
        snap.summary = f"RSI={snap.rsi_14} 超卖区，技术反弹潜力"
    elif snap.close and snap.ma_20 and snap.close > snap.ma_20:
        snap.signal = SignalDirection.NEUTRAL
        snap.summary = "价格在 MA20 上方，短期趋势偏多"
    else:
        snap.signal = SignalDirection.NEUTRAL
        snap.summary = "技术面中性"

    return snap


def generate_comprehensive_report(
    ticker: str,
    earnings_date: str,
    beat: EarningsBeatAnalysis,
    sentiment: SentimentAnalysis,
    pattern: HistoricalPattern,
    technical: TechnicalSnapshot,
) -> EarningsAnalysisReport:
    """Combine all analysis dimensions into a final report with strategy recommendation."""
    report = EarningsAnalysisReport(
        ticker=ticker,
        earnings_date=earnings_date,
        beat_analysis=beat,
        sentiment_analysis=sentiment,
        historical_pattern=pattern,
        technical_snapshot=technical,
    )

    # Scoring: each dimension contributes to final signal
    signal_scores = {SignalDirection.BULLISH: 0, SignalDirection.BEARISH: 0, SignalDirection.NEUTRAL: 0}

    for analysis, weight in [
        (beat, 0.30), (sentiment, 0.25), (technical, 0.15),
    ]:
        if analysis and analysis.signal:
            signal_scores[analysis.signal] += weight

    # Historical pattern: use avg_return_1d direction
    if pattern and pattern.avg_return_1d is not None:
        if pattern.avg_return_1d > 0.5:
            signal_scores[SignalDirection.BULLISH] += 0.15
        elif pattern.avg_return_1d < -0.5:
            signal_scores[SignalDirection.BEARISH] += 0.15
        else:
            signal_scores[SignalDirection.NEUTRAL] += 0.15
    else:
        signal_scores[SignalDirection.NEUTRAL] += 0.15

    # Remaining weight: confidence factor
    signal_scores[SignalDirection.NEUTRAL] += 0.15

    # Determine final signal
    max_score = max(signal_scores.values())
    report.confidence = round(max_score, 2)
    report.final_signal = max(signal_scores, key=signal_scores.get)

    # Strategy selection
    if report.final_signal == SignalDirection.BULLISH and pattern.pattern_label == "惯涨":
        report.strategy = StrategyLabel.GAP_CHASE
        report.trade_rationale = (
            f"{ticker} 财报双因子利多（情绪+beat），且历史上 {pattern.beat_rate_pct}% 的财报后上涨。"
            f"策略：跳空追进，止损 {STOP_LOSS_PCT*100:.0f}%，止盈 {TAKE_PROFIT_PCT*100:.0f}%。"
        )
    elif report.final_signal == SignalDirection.BULLISH:
        report.strategy = StrategyLabel.GAP_CHASE
        report.trade_rationale = f"{ticker} 财报信号偏多，建议小仓位追涨。止损 -3%，止盈 +5%。"
    elif report.final_signal == SignalDirection.BEARISH and pattern.pattern_label == "惯跌":
        report.strategy = StrategyLabel.FADE
        report.trade_rationale = (
            f"{ticker} 财报利空 + 历史惯性下跌。策略：反向操作（做空），止损 -3%，止盈 +5%。"
        )
    elif report.final_signal == SignalDirection.BEARISH:
        report.strategy = StrategyLabel.WATCH
        report.trade_rationale = f"{ticker} 财报信号偏空但历史规律不明确，建议观望。"
    elif technical.signal == SignalDirection.BEARISH and technical.rsi_14 and technical.rsi_14 > 70:
        report.strategy = StrategyLabel.WATCH
        report.trade_rationale = f"{ticker} 财报中性但技术面超买 (RSI={technical.rsi_14})，追高风险大，建议观望。"
    elif pattern.avg_return_1d is not None and pattern.avg_return_1d < -1.0:
        report.strategy = StrategyLabel.MEAN_REVERT
        report.trade_rationale = (
            f"{ticker} 历史财报后平均下跌 {pattern.avg_return_1d}%，存在均值回归机会。"
            f"策略：等待跳空下跌后择机介入。"
        )
    else:
        report.strategy = StrategyLabel.WATCH
        report.trade_rationale = f"{ticker} 多维度信号不一致或置信度不足，建议观望。"

    # Risk flags
    if technical.rsi_14 and technical.rsi_14 > 70:
        report.risk_flags.append(f"RSI超买 ({technical.rsi_14})")
    if pattern.quarters_analyzed < 3:
        report.risk_flags.append(f"历史数据不足 ({pattern.quarters_analyzed}个季度)")
    if beat.eps_surprise_pct and abs(beat.eps_surprise_pct) > 20:
        report.risk_flags.append(f"业绩波动异常 (EPS偏离{beat.eps_surprise_pct}%)")

    from .config import SAFETY_NOTICE
    report.safety_notice = SAFETY_NOTICE

    return report


# Local imports for STOP_LOSS_PCT, TAKE_PROFIT_PCT at module bottom
from .config import STOP_LOSS_PCT, TAKE_PROFIT_PCT
