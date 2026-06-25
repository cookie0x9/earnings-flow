"""
EarningsFlow Streamlit Dashboard — 财报季AI事件驱动交易Agent
Bitget AI Base Camp S1 · Track 3 · US Stock AI Trading
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from earnings_flow.config import (
    BITGET_TOKENIZED_STOCKS,
    PRIMARY_WATCHLIST,
    STRATEGY_LABELS,
    SAFETY_NOTICE,
    AGENT_HUB_CAPABILITIES,
)
from earnings_flow.data import (
    get_earnings_calendar,
    get_price_history,
    get_post_earnings_price_moves,
    get_beat_rate,
)
from earnings_flow.pipeline import run_earnings_pipeline, run_single_ticker_pipeline
from earnings_flow.paper_trading import PaperTradingLogger, PaperTradingAccount
from earnings_flow.analysis import (
    EarningsAnalysisReport,
    SignalDirection,
    StrategyLabel,
    analyze_earnings_beat,
    analyze_sentiment,
    compute_technical_snapshot,
    generate_comprehensive_report,
)

st.set_page_config(
    page_title="EarningsFlow — 财报季AI事件驱动交易Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .signal-bullish { color: #00C853; font-weight: bold; }
    .signal-bearish { color: #FF1744; font-weight: bold; }
    .signal-neutral { color: #FFD600; font-weight: bold; }
    .metric-card {
        background: #1A1A2E; border-radius: 8px; padding: 16px;
        border: 1px solid #2A2A3E; margin: 4px 0;
    }
    .trade-row { font-family: 'Courier New', monospace; font-size: 0.9em; }
    .risk-flag { color: #FF6D00; font-size: 0.85em; }
    .safety-banner {
        background: #2A1A00; border: 1px solid #FF6D00; border-radius: 6px;
        padding: 8px 16px; margin: 8px 0; font-size: 0.85em; color: #FFB74D;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "paper_logger" not in st.session_state:
    st.session_state.paper_logger = PaperTradingLogger(
        log_dir=str(Path(__file__).resolve().parent / "evidence")
    )
if "reports" not in st.session_state:
    st.session_state.reports = []
if "selected_tickers" not in st.session_state:
    st.session_state.selected_tickers = PRIMARY_WATCHLIST[:5]


# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📊 EarningsFlow")
    st.caption("Bitget AI Base Camp S1 · Track 3")
    st.caption("US Stock AI Trading")

    st.markdown("---")
    st.subheader("🔍 分析设置")

    use_mock = st.checkbox("使用模拟数据", value=True, help="使用本地 mock 数据（无需网络）")

    selected_tickers = st.multiselect(
        "跟踪标的",
        options=PRIMARY_WATCHLIST,
        default=st.session_state.selected_tickers,
        help="选择 Bitget 代币化美股进行财报分析",
    )
    st.session_state.selected_tickers = selected_tickers

    lookback = st.slider("历史回顾季度", 2, 8, 4, help="分析过去几个财报季的数据")

    eps_override = st.expander("📝 自定义财报数据")
    with eps_override:
        custom_ticker = st.selectbox("标的", PRIMARY_WATCHLIST, key="custom_ticker")
        custom_eps_actual = st.number_input("EPS 实际值", value=0.0, step=0.01, format="%.2f")
        custom_eps_est = st.number_input("EPS 预期值", value=0.0, step=0.01, format="%.2f")
        custom_rev_actual = st.number_input("营收实际值 (B)", value=0.0, step=0.1, format="%.1f")
        custom_rev_est = st.number_input("营收预期值 (B)", value=0.0, step=0.1, format="%.1f")
        custom_sentiment = st.text_area("电话会/管理层摘要", placeholder="输入电话会文本或管理层指引摘要...")

    st.markdown("---")
    st.subheader("🤖 Agent Hub 能力")
    for cap_id, cap_info in AGENT_HUB_CAPABILITIES.items():
        st.caption(f"**{cap_id}** — {cap_info['purpose']} `[{cap_info['status']}]`")

    st.markdown("---")
    st.caption(SAFETY_NOTICE)


# --- Main Content ---
st.title("📊 EarningsFlow")
st.subheader("财报季AI事件驱动交易Agent")
st.caption(f"Bitget 代币化美股 · {len(PRIMARY_WATCHLIST)} 只标的 · Paper Trading Only")

st.markdown(f'<div class="safety-banner">{SAFETY_NOTICE}</div>', unsafe_allow_html=True)

tabs = st.tabs([
    "📅 财报日历",
    "🔬 个股深度分析",
    "📈 策略信号面板",
    "📋 交易日志",
    "📊 绩效统计",
    "ℹ️ 关于",
])

# === Tab 1: Earnings Calendar ===
with tabs[0]:
    st.subheader("Bitget 代币化美股 — 财报日历")

    col1, col2 = st.columns([2, 1])
    with col1:
        if use_mock:
            # Mock earnings calendar with realistic dates
            base = datetime.now()
            mock_calendar = pd.DataFrame([
                {"ticker": t, "earnings_date": base + timedelta(days=i * 3 - 5),
                 "eps_estimate": round(0.5 + i * 0.3, 2),
                 "revenue_estimate": round(10.0 + i * 5.0, 1),
                 "eps_actual": round(0.5 + i * 0.3 + (i % 3 - 1) * 0.15, 2),
                 "surprise_pct": round((i % 3 - 1) * 8.0, 1)}
                for i, t in enumerate(selected_tickers)
            ])
        else:
            mock_calendar = get_earnings_calendar(selected_tickers)

        if not mock_calendar.empty:
            mock_calendar["earnings_date"] = pd.to_datetime(mock_calendar["earnings_date"])
            mock_calendar_display = mock_calendar.copy()
            mock_calendar_display["earnings_date"] = mock_calendar_display["earnings_date"].dt.strftime("%Y-%m-%d")

            def color_surprise(val):
                if isinstance(val, (int, float)):
                    if val > 5:
                        return "color: #00C853"
                    elif val < -5:
                        return "color: #FF1744"
                return ""

            styled = mock_calendar_display.style.map(
                color_surprise, subset=["surprise_pct"]
            ) if "surprise_pct" in mock_calendar_display.columns else mock_calendar_display
            st.dataframe(mock_calendar_display, use_container_width=True, hide_index=True)
        else:
            st.warning("无法获取财报日历数据。请在非美股财报季时使用模拟数据。")

    with col2:
        st.metric("跟踪标的数", len(selected_tickers))
        upcoming = len(mock_calendar[mock_calendar["earnings_date"] >= datetime.now()]) if not mock_calendar.empty else 0
        st.metric("即将发布", upcoming)
        st.metric("Bitget 代币化美股总量", len(BITGET_TOKENIZED_STOCKS))
        st.caption("数据源: yFinance (public) + SEC EDGAR (public)")
        st.caption("Bitget 代币化美股标的标识基于公开产品页面")

# === Tab 2: Deep Analysis ===
with tabs[1]:
    st.subheader("个股深度分析")

    analysis_ticker = st.selectbox("选择标的", selected_tickers, key="deep_ticker")

    col_run, col_custom = st.columns([1, 3])
    with col_run:
        run_analysis = st.button("▶️ 运行分析", type="primary", use_container_width=True)

    if run_analysis or st.session_state.reports:
        if run_analysis:
            with st.spinner(f"正在分析 {analysis_ticker} ..."):
                if eps_override and custom_eps_actual != 0:
                    report = run_single_ticker_pipeline(
                        analysis_ticker,
                        eps_actual=custom_eps_actual or None,
                        eps_estimate=custom_eps_est or None,
                        revenue_actual=custom_rev_actual or None,
                        revenue_estimate=custom_rev_est or None,
                        transcript_text=custom_sentiment,
                        lookback_quarters=lookback,
                    )
                else:
                    report = run_single_ticker_pipeline(
                        analysis_ticker,
                        lookback_quarters=lookback,
                    )
                # Update or add report
                existing = [r for r in st.session_state.reports if r.ticker != analysis_ticker]
                st.session_state.reports = existing + [report]
        else:
            report = next(
                (r for r in st.session_state.reports if r.ticker == analysis_ticker), None
            )

        if report:
            # Signal banner
            signal_color = {
                SignalDirection.BULLISH: "#00C853",
                SignalDirection.BEARISH: "#FF1744",
                SignalDirection.NEUTRAL: "#FFD600",
            }[report.final_signal]
            signal_emoji = {
                SignalDirection.BULLISH: "🟢",
                SignalDirection.BEARISH: "🔴",
                SignalDirection.NEUTRAL: "🟡",
            }[report.final_signal]
            strategy_label = STRATEGY_LABELS.get(report.strategy.value, report.strategy.value)

            st.markdown(f"""
            <div style="background:#1A1A2E;border:2px solid {signal_color};border-radius:12px;padding:20px;margin:12px 0;">
                <h2 style="margin:0;color:{signal_color};">{signal_emoji} {report.final_signal.value.upper()} → 策略: {strategy_label}</h2>
                <p style="margin:8px 0 0 0;color:#AAA;">置信度: {report.confidence:.0%}</p>
            </div>
            """, unsafe_allow_html=True)

            # Four analysis cards
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.markdown("**📊 Beat/Miss 分析**")
                if report.beat_analysis:
                    b = report.beat_analysis
                    st.metric("EPS Surprise", f"{b.eps_surprise_pct:+.1f}%" if b.eps_surprise_pct else "N/A")
                    st.metric("Revenue Surprise", f"{b.revenue_surprise_pct:+.1f}%" if b.revenue_surprise_pct else "N/A")
                    st.caption(b.summary)
                else:
                    st.caption("数据不可用")

            with c2:
                st.markdown("**🗣️ 情绪分析**")
                if report.sentiment_analysis:
                    s = report.sentiment_analysis
                    st.metric("情绪评分", f"{s.sentiment_score:.2f}" if s.sentiment_score else "N/A")
                    st.metric("Guidance", s.guidance_signal.value if s.guidance_signal else "N/A")
                    st.caption(s.summary)
                    if s.key_positives:
                        st.caption(f"✅ {', '.join(s.key_positives[:3])}")
                    if s.key_risks:
                        st.caption(f"⚠️ {', '.join(s.key_risks[:3])}")
                else:
                    st.caption("数据不可用")

            with c3:
                st.markdown("**📈 历史规律**")
                if report.historical_pattern:
                    p = report.historical_pattern
                    st.metric("分析季度", p.quarters_analyzed)
                    st.metric("上涨概率", f"{p.beat_rate_pct}%" if p.beat_rate_pct else "N/A")
                    st.metric("Avg 1D Return", f"{p.avg_return_1d:+.2f}%" if p.avg_return_1d else "N/A")
                    st.caption(p.pattern_label)
                else:
                    st.caption("数据不可用")

            with c4:
                st.markdown("**🔧 技术面**")
                if report.technical_snapshot:
                    tech = report.technical_snapshot
                    st.metric("RSI-14", f"{tech.rsi_14}" if tech.rsi_14 else "N/A")
                    st.metric("Close vs MA20", f"${tech.close:.2f}" if tech.close else "N/A")
                    st.metric("Volatility (30d)", f"{tech.volatility_30d}%" if tech.volatility_30d else "N/A")
                    st.caption(tech.summary)
                else:
                    st.caption("数据不可用")

            # Trade rationale
            st.markdown("---")
            st.markdown("### 🎯 交易决策")
            st.info(report.trade_rationale)

            # Risk flags
            if report.risk_flags:
                st.warning("⚠️ 风险标记: " + " | ".join(report.risk_flags))

            # Price chart
            st.markdown("---")
            st.markdown(f"### 📈 {analysis_ticker} 价格走势")
            try:
                price_df = get_price_history(analysis_ticker, period="6mo")
                if not price_df.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=price_df.index, open=price_df["Open"], high=price_df["High"],
                        low=price_df["Low"], close=price_df["Close"],
                        name=analysis_ticker,
                    ))
                    fig.update_layout(
                        template="plotly_dark", height=400, margin=dict(l=0, r=0, t=0, b=0),
                        xaxis_rangeslider_visible=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.caption("价格数据不可用")
            except Exception:
                st.caption("价格图表加载失败")

            # Historical moves detail
            if report.historical_pattern and report.historical_pattern.recent_moves:
                st.markdown("### 📋 历史财报后走势")
                moves_df = pd.DataFrame(report.historical_pattern.recent_moves)
                st.dataframe(moves_df, use_container_width=True, hide_index=True)


# === Tab 3: Strategy Signals ===
with tabs[2]:
    st.subheader("策略信号面板")

    col_refresh, col_auto = st.columns([1, 3])
    with col_refresh:
        refresh_all = st.button("🔄 刷新全部信号", type="primary", use_container_width=True)

    if refresh_all:
        with st.spinner(f"正在分析 {len(selected_tickers)} 只标的..."):
            st.session_state.reports = run_earnings_pipeline(
                selected_tickers[:5], lookback_quarters=lookback
            )

    if st.session_state.reports:
        # Summary cards in a row
        cols = st.columns(len(st.session_state.reports))
        for i, report in enumerate(st.session_state.reports):
            with cols[i]:
                sig = report.final_signal
                emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "🟡"}[sig.value]
                strat = STRATEGY_LABELS.get(report.strategy.value, report.strategy.value)
                st.markdown(f"""
                <div style="background:#1A1A2E;border-radius:8px;padding:12px;text-align:center;">
                    <h3>{emoji} {report.ticker}</h3>
                    <p style="font-size:1.2em;font-weight:bold;">{strat}</p>
                    <p style="color:#AAA;font-size:0.85em;">置信度: {report.confidence:.0%}</p>
                </div>
                """, unsafe_allow_html=True)

        # Full table
        st.markdown("---")
        st.markdown("### 📊 信号详情")

        signal_data = []
        for r in st.session_state.reports:
            d = r.to_dict()
            d["beat"] = r.beat_analysis.summary if r.beat_analysis else ""
            d["sentiment"] = r.sentiment_analysis.summary if r.sentiment_analysis else ""
            d["pattern"] = r.historical_pattern.summary if r.historical_pattern else ""
            signal_data.append(d)

        signal_df = pd.DataFrame(signal_data)
        display_cols = ["ticker", "final_signal", "confidence", "strategy_label", "trade_rationale"]
        display_cols = [c for c in display_cols if c in signal_df.columns]
        st.dataframe(
            signal_df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "final_signal": st.column_config.TextColumn("信号"),
                "confidence": st.column_config.ProgressColumn("置信度", format="%.0f%%", min_value=0, max_value=1),
                "strategy_label": st.column_config.TextColumn("策略"),
                "trade_rationale": st.column_config.TextColumn("决策理由", width="large"),
            },
        )
    else:
        st.info("👈 点击「刷新全部信号」开始分析，或在「个股深度分析」中逐一分析")

    # Execute paper trade
    st.markdown("---")
    st.markdown("### 📝 执行模拟交易")
    st.caption("基于当前信号执行 paper-trading")

    exec_col1, exec_col2, exec_col3 = st.columns(3)
    with exec_col1:
        exec_ticker = st.selectbox("标的", selected_tickers, key="exec_ticker")
    with exec_col2:
        exec_direction = st.selectbox("方向", ["LONG", "SHORT"])
    with exec_col3:
        exec_qty = st.number_input("数量 (股)", value=10, min_value=1, step=1, key="exec_qty")

    if st.button("📝 执行 Paper Trade", type="primary"):
        report = next((r for r in st.session_state.reports if r.ticker == exec_ticker), None)
        if report:
            price_df = get_price_history(exec_ticker, period="5d")
            price = float(price_df["Close"].iloc[-1]) if not price_df.empty else 100.0

            trade = st.session_state.paper_logger.account.open_position(
                exec_ticker, exec_direction, price, exec_qty, report
            )
            if trade:
                st.session_state.paper_logger.log_trade(trade)
                st.success(f"✅ Paper Trade 已执行: {exec_ticker} {exec_direction} {exec_qty}股 @ ${price:.2f}")
                st.json(trade.to_dict())
            else:
                st.error("❌ 交易被风控拒绝（仓位超限或资金不足）")
        else:
            st.warning("请先运行该标的的分析")


# === Tab 4: Trading Log ===
with tabs[3]:
    st.subheader("Paper Trading 日志")
    st.caption("Track 3 要求字段: timestamp, asset, direction, price, quantity, balance change")

    trade_df = st.session_state.paper_logger.load_log()

    if not trade_df.empty:
        # Stats row
        closed = trade_df[trade_df["pnl"].notna()] if "pnl" in trade_df.columns else pd.DataFrame()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("总交易数", len(trade_df))
        with c2:
            st.metric("已平仓", len(closed))
        with c3:
            if len(closed) > 0:
                st.metric("胜率", f"{len(closed[closed['pnl'] > 0]) / len(closed) * 100:.1f}%")
        with c4:
            if len(closed) > 0:
                st.metric("总PnL", f"${closed['pnl'].sum():.2f}")

        st.dataframe(trade_df, use_container_width=True, hide_index=True)

        # Export
        st.download_button(
            "📥 下载交易日志 (CSV)",
            trade_df.to_csv(index=False),
            "earnings_flow_paper_trading_log.csv",
            "text/csv",
        )
    else:
        st.info("暂无交易记录。在「策略信号面板」中执行模拟交易。")

    # Manual close
    st.markdown("---")
    st.markdown("### 平仓操作")
    open_positions = st.session_state.paper_logger.account.positions
    if open_positions:
        close_ticker = st.selectbox("选择持仓", list(open_positions.keys()), key="close_ticker")
        close_price = st.number_input("平仓价格", value=100.0, step=0.01, format="%.2f", key="close_price")
        close_reason = st.text_input("平仓理由", placeholder="止盈/止损/到期/手动", key="close_reason")

        if st.button("🔒 平仓", type="primary"):
            trade = st.session_state.paper_logger.account.close_position(
                close_ticker, close_price, close_reason
            )
            if trade:
                st.session_state.paper_logger.log_trade(trade)
                st.success(f"✅ 已平仓 {close_ticker}: PnL ${trade.pnl:.2f} ({trade.pnl_pct:+.2f}%)")
                st.rerun()
            else:
                st.error("平仓失败")
    else:
        st.caption("当前无持仓")


# === Tab 5: Performance Statistics ===
with tabs[4]:
    st.subheader("绩效统计")

    stats = st.session_state.paper_logger.get_performance_stats()

    if stats.get("total_trades", 0) > 0:
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("总交易", stats["total_trades"])
        with m2:
            st.metric("胜率", f"{stats['win_rate_pct']}%")
        with m3:
            st.metric("总PnL", f"${stats['total_pnl']:.2f}")
        with m4:
            st.metric("最佳交易", f"${stats['best_trade']:.2f}")
        with m5:
            st.metric("总回报", f"{stats['total_return_pct']:.2f}%")

        # Strategy breakdown chart
        if "by_strategy" in stats and stats["by_strategy"]:
            by_strat = pd.DataFrame(stats["by_strategy"])
            if "strategy" in by_strat.columns:
                by_strat["label"] = by_strat["strategy"].map(STRATEGY_LABELS).fillna(by_strat["strategy"])
                c1, c2 = st.columns(2)
                with c1:
                    fig = px.bar(
                        by_strat, x="label", y="total_pnl", color="label",
                        title="策略PnL分布",
                        labels={"label": "策略", "total_pnl": "PnL ($)"},
                    )
                    fig.update_layout(template="plotly_dark", height=350)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = px.bar(
                        by_strat, x="label", y="win_rate", color="label",
                        title="策略胜率对比",
                        labels={"label": "策略", "win_rate": "胜率 (%)"},
                    )
                    fig.update_layout(template="plotly_dark", height=350)
                    st.plotly_chart(fig, use_container_width=True)

        # Portfolio equity curve (mock)
        st.markdown("### 📈 账户权益曲线")
        if not trade_df.empty and "balance_after" in trade_df.columns:
            balance_df = trade_df[["timestamp", "balance_after"]].dropna()
            if not balance_df.empty:
                balance_df["timestamp"] = pd.to_datetime(balance_df["timestamp"])
                balance_df = balance_df.sort_values("timestamp")
                fig = px.line(
                    balance_df, x="timestamp", y="balance_after",
                    title="Account Equity (Paper)",
                    labels={"timestamp": "时间", "balance_after": "权益 ($)"},
                )
                fig.update_layout(template="plotly_dark", height=350)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无交易数据。请先在「策略信号面板」中执行模拟交易。")

    st.caption("所有统计数据基于 paper trading 日志，不代表真实交易表现。")


# === Tab 6: About ===
with tabs[5]:
    st.subheader("关于 EarningsFlow")

    st.markdown("""
    ### 📊 EarningsFlow — 财报季AI事件驱动交易Agent

    **Bitget AI Base Camp Season 1 · Track 3 · US Stock AI Trading**

    #### 核心理念

    Bitget 代币化美股财报季成交量暴涨 4468%。EarningsFlow 是专为这一时刻设计的 AI 事件驱动 Agent——不是简单的 "beat=买入"，而是通过多维度财报分析 + 历史规律对比，生成可执行的事件驱动交易信号。

    #### 分析维度

    | 维度 | 方法 |
    | --- | --- |
    | **Beat/Miss** | EPS & 营收 实际 vs 预期 |
    | **情绪分析** | 电话会文本语调 + 管理层指引 |
    | **历史规律** | 过去 4-8 个季度财报后走势对比 |
    | **技术面** | RSI, MA, 波动率, 成交量比 |

    #### 策略分类

    - 🟢 **跳空追进** (Gap Chase): 双因子利多 + 历史惯性上涨
    - 🟡 **均值回归** (Mean Revert): 财报后超跌反弹机会
    - 🔴 **反向操作** (Fade): 财报利空 + 惯性下跌
    - ⚪ **观望** (Watch): 多维度信号不一致

    #### Agent Hub 能力

    """)

    for cap_id, cap_info in AGENT_HUB_CAPABILITIES.items():
        st.markdown(f"- **{cap_id}**: {cap_info['purpose']} `[{cap_info['status']}]`")

    st.markdown("""
    #### 安全声明

    - ⚠️ 所有交易信号均为 **paper trading（模拟盘）**，不涉及真实资金
    - ⚠️ 不存储任何 API Key、密码、私钥、UID 或账户信息
    - ⚠️ 分析报告不构成投资建议
    - ⚠️ 历史回测不代表未来表现
    - 📊 数据来源: yFinance (public), SEC EDGAR (public)

    #### Bitget 连接

    分析标的覆盖 Bitget 上交易量最大的代币化美股（TSLA, META, AAPL, NVDA, MSFT, GOOGL, AMZN, MSTR 等），策略利用 Bitget 代币化美股期货的 5x24 交易特性。

    ---
    *Bitget AI Base Camp S1 · 2026*
    """)
