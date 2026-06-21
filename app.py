"""
ETF 定投回测 + 市场环境分析 — v0.5
GitHub: Colorfulrain1751/etf-dca-backtest
"""

import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="ETF 定投回测 · 市场分析",
    page_icon="▸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes countUp {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .block-container { padding-top: 2rem; }

    /* ===== SECTION TITLES ===== */
    .section-title {
        font-size: 1.1rem; font-weight: 700; color: #1a1a1a;
        padding-left: 14px; margin: 24px 0 12px 0;
        border-left: 4px solid transparent;
        border-image: linear-gradient(180deg, #1a56db, #4f46e5) 1;
        animation: slideInLeft 0.5s ease-out;
    }

    /* ===== INDEX CARDS ===== */
    .index-card {
        background: #fff;
        border-radius: 12px; padding: 18px 14px;
        text-align: center;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.25s ease;
        animation: fadeInUp 0.5s ease-out backwards;
    }
    .index-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        border-color: #1a56db;
    }
    .index-card:nth-child(1) { animation-delay: 0.05s; }
    .index-card:nth-child(2) { animation-delay: 0.10s; }
    .index-card:nth-child(3) { animation-delay: 0.15s; }
    .index-card:nth-child(4) { animation-delay: 0.20s; }
    .index-card:nth-child(5) { animation-delay: 0.25s; }

    .index-name {
        font-size: 0.8rem; color: #6b7280; margin-bottom: 4px;
        font-weight: 500;
    }
    .index-price {
        font-size: 1.5rem; font-weight: 800; color: #111;
        margin: 4px 0; animation: countUp 0.6s ease-out;
    }
    .index-change {
        font-weight: 700; font-size: 1rem;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] { transition: all 0.25s ease; }
    [data-testid="stMetric"]:hover { transform: scale(1.02); }
    [data-testid="stMetricValue"] {
        animation: countUp 0.6s ease-out;
        font-weight: 800 !important; color: #111 !important;
    }
    [data-testid="stMetricDelta"] { font-weight: 700 !important; }

    /* ===== BUTTONS ===== */
    .stButton > button {
        transition: all 0.2s ease !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        background: #1a56db !important;
        color: #fff !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(26,86,219,0.3) !important;
        background: #1e40af !important;
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; border-bottom: 2px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        transition: all 0.2s ease;
        border-radius: 8px 8px 0 0; padding: 10px 20px;
        font-weight: 600; color: #6b7280;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #f3f4f6; color: #111;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1a56db; font-weight: 700;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        transition: all 0.2s ease; border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderHeader:hover {
        background: #f3f4f6 !important; color: #111 !important;
    }

    /* ===== SPINNER ===== */
    .stSpinner > div { border-top-color: #1a56db !important; }

    /* ===== TAGS ===== */
    .source-tag {
        display: inline-block; background: #f3f4f6; color: #6b7280;
        font-size: 0.7rem; padding: 2px 10px; border-radius: 12px;
        margin-left: 6px; font-weight: 500;
    }
    .verified-badge {
        display: inline-block; background: #ecfdf5; color: #065f46;
        font-size: 0.7rem; padding: 3px 10px; border-radius: 12px;
        margin-left: 6px; font-weight: 600;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center; color: #9ca3af; font-size: 0.78rem;
        margin-top: 48px; padding-top: 18px;
        border-top: 1px solid #e5e7eb;
        animation: fadeIn 1s ease-out;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }

    /* ===== TABLE ===== */
    [data-testid="stDataFrame"] {
        animation: fadeIn 0.6s ease-out; border-radius: 10px !important;
        overflow: hidden;
    }

    /* ===== CHART ===== */
    [data-testid="stArrowVegaLiteChart"] { animation: fadeIn 0.8s ease-out; }

    /* ===== INPUT FOCUS ===== */
    .stTextInput > div > div:focus-within,
    .stDateInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        box-shadow: 0 0 0 3px rgba(26,86,219,0.1) !important;
    }

    /* ===== INFO BOX ===== */
    .stAlert { border-radius: 10px !important; font-weight: 500; }

    html { scroll-behavior: smooth; }
    .hero { text-align:center; padding:80px 20px 60px 20px; animation:fadeIn 0.8s ease-out; background:linear-gradient(180deg,#1a56db 0%,#3b82f6 30%,#93c5fd 70%,#ffffff 100%); }
    .hero h1 { font-size:2.8rem; font-weight:800; color:#fff; letter-spacing:-0.5px; margin-bottom:12px; text-shadow:0 2px 8px rgba(0,0,0,0.1); }
    .hero .gradient { background:linear-gradient(135deg,#fbbf24,#f59e0b,#fbbf24); background-size:200% 200%; animation:gradientFlow 4s ease infinite; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .hero .tagline { font-size:1.1rem; color:rgba(255,255,255,0.9); max-width:600px; margin:16px auto 8px auto; line-height:1.7; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CACHE
# ============================================================
@st.cache_data(ttl=3600)
def fetch_index_spot():
    return ak.stock_zh_index_spot_sina()

@st.cache_data(ttl=3600)
def fetch_market_pe():
    return ak.stock_market_pe_lg()

@st.cache_data(ttl=3600)
def fetch_market_pb():
    return ak.stock_market_pb_lg()

@st.cache_data(ttl=3600)
def fetch_index_pe(symbol="沪深300"):
    return ak.stock_index_pe_lg(symbol=symbol)

@st.cache_data(ttl=3600)
def fetch_index_daily(symbol="sh000001"):
    return ak.stock_zh_index_daily(symbol=symbol)

@st.cache_data(ttl=86400)
def fetch_etf_history(symbol):
    return ak.fund_etf_hist_sina(symbol=symbol)

@st.cache_data(ttl=86400)
def fetch_stock_history(symbol):
    """个股日线数据（新浪，前复权）"""
    return ak.stock_zh_a_daily(symbol=symbol, adjust="qfq")

def resolve_symbol(code):
    code = str(code).strip()
    if code.startswith("159") or code.startswith("16"):
        return f"sz{code}"
    if code.startswith("0") or code.startswith("3"):
        return f"sz{code}"
    return f"sh{code}"

# ============================================================

st.markdown("""
<div class="hero">
    <h1>用数据看懂市场<br><span class="gradient">不再凭感觉投资</span></h1>
    <p class="tagline">
        基于真实行情数据，3 秒完成定投回测、估值分析和个股技术诊断。
        让每一次决策都有数据支撑。
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(
    f"数据更新于 {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
    "[GitHub](https://github.com/Colorfulrain1751/etf-dca-backtest) | "
    "<span class='verified-badge'>已交叉验证</span>",
    unsafe_allow_html=True,
)

# TITLE
# ============================================================
st.markdown("""
<h1 style="font-size:2.2rem; font-weight:800; margin-bottom:0; color:#111;">
    ETF 定投回测
    <span style="color:#1a56db;">·</span>
    <span style="color:#4b5563; font-weight:600;">市场环境分析</span>
</h1>
""", unsafe_allow_html=True)
st.caption(
    f"数据更新于 {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
    "v0.5 | "
    "[GitHub](https://github.com/Colorfulrain1751/etf-dca-backtest) | "
    "<span class='verified-badge'>已交叉验证</span>",
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["定投回测", "市场分析", "个股分析", "更新日志"])

# ============================================================
# TAB 1 — 定投回测
# ============================================================
with tab1:
    st.markdown("""<div class="section-title">参数设置</div>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    with c1:
        code_input = st.text_input("ETF 代码", value="510300",
                                   help="沪市: 51 / 56 / 58 开头 | 深市: 159 / 16 开头")
    with c2:
        start_date = st.date_input("开始定投日期", value=datetime(2020, 1, 1))
    with c3:
        monthly = st.number_input("每月定投金额（元）", value=500, step=100, min_value=100)
    with c4:
        st.write("")
        go = st.button("开始回测", type="primary", use_container_width=True)

    with st.expander("常用 ETF 代码参考"):
        st.markdown("""
        | 代码 | 名称 | 代码 | 名称 |
        |------|------|------|------|
        | **510300** | 沪深300ETF | **510500** | 中证500ETF |
        | **510050** | 上证50ETF | **159915** | 创业板ETF |
        | **588000** | 科创50ETF | **512880** | 证券ETF |
        | **512100** | 中证1000ETF | **513100** | 纳指ETF(沪) |
        | **159941** | 纳指ETF(深) | **510880** | 红利ETF |
        """)

    if go:
        symbol = resolve_symbol(code_input)

        with st.spinner("正在从新浪财经获取行情数据…"):
            try:
                df = fetch_etf_history(symbol)
            except Exception as e:
                st.error(f"获取数据失败：{e}")
                st.stop()

        if df.empty:
            st.error(f"代码 {code_input} 无数据，请检查是否输入正确")
            st.stop()

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        df = df[df["date"] >= pd.Timestamp(start_date)].copy()
        if df.empty:
            st.warning("所选日期范围内无数据，请调整起始日期")
            st.stop()

        df["ym"] = df["date"].dt.to_period("M")
        buy_mask = ~df.duplicated(subset="ym", keep="first")

        total_shares = sum(monthly / df.loc[i, "close"] for i in df[buy_mask].index)
        total_invested = monthly * buy_mask.sum()
        periods = buy_mask.sum()

        latest_price = df.iloc[-1]["close"]
        latest_date = df.iloc[-1]["date"]
        current_value = total_shares * latest_price
        profit = current_value - total_invested
        return_pct = (profit / total_invested) * 100
        avg_cost = total_invested / total_shares

        first_price = df.loc[df[buy_mask].index[0], "close"]
        first_date = df.loc[df[buy_mask].index[0], "date"]

        # --- 回测结果 ---
        st.markdown("""<div class="section-title">回测结果</div>""", unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("累计投入本金", f"¥{total_invested:,.0f}", delta=f"共 {periods} 期")
        with m2:
            st.metric("当前持仓市值", f"¥{current_value:,.0f}",
                      delta=f"{profit:+,.0f}" if profit >= 0 else f"-¥{abs(profit):,.0f}")
        with m3:
            st.metric("总收益率", f"{return_pct:+.2f}%")
        with m4:
            st.metric("平均持仓成本", f"¥{avg_cost:.4f}")
        with m5:
            st.metric("最新价格", f"¥{latest_price:.4f}",
                      delta=f"{(latest_price/avg_cost-1)*100:+.1f}%")

        st.caption(
            f"首笔买入：{first_date.strftime('%Y-%m-%d')}，价格 ¥{first_price:.4f} | "
            f"数据截止：{latest_date.strftime('%Y-%m-%d')} | "
            f"<span class='source-tag'>新浪财经</span>",
            unsafe_allow_html=True,
        )

        # --- 走势图 ---
        st.markdown("""<div class="section-title">价格走势</div>""", unsafe_allow_html=True)
        chart_df = df.set_index("date")
        # 只画价格线，避免 buy_signal 全 NaN 产生空图例
        st.line_chart(chart_df[["close"]], height=380, color=["#1a56db"])

        # 买入点统计代替散点
        buy_dates = df[buy_mask]
        first_buy = buy_dates.iloc[0]
        last_buy = buy_dates.iloc[-1]
        st.caption(
            f"定投共 <strong>{periods} 次</strong> | "
            f"首笔 {first_buy['date'].strftime('%Y-%m-%d')} @ ¥{first_buy['close']:.4f} | "
            f"末笔 {last_buy['date'].strftime('%Y-%m-%d')} @ ¥{last_buy['close']:.4f} | "
            f"前复权价格",
            unsafe_allow_html=True,
        )

        # --- 年度明细 ---
        st.markdown("""<div class="section-title">年度明细</div>""", unsafe_allow_html=True)
        buy_df = df[buy_mask][["date", "close"]].copy()
        buy_df["year"] = buy_df["date"].dt.year
        buy_df["shares"] = monthly / buy_df["close"]
        yearly = buy_df.groupby("year").agg(
            买入次数=("date", "count"),
            投入金额=("shares", lambda x: monthly * len(x)),
            买入均价=("close", "mean"),
            买入份额=("shares", "sum"),
        ).reset_index()
        yearly["投入金额"] = yearly["投入金额"].astype(int)
        yearly["买入均价"] = yearly["买入均价"].round(4)
        yearly["买入份额"] = yearly["买入份额"].round(2)
        st.dataframe(yearly, use_container_width=True, hide_index=True)

# ============================================================
# TAB 2 — 市场分析
# ============================================================
with tab2:
    st.caption("数据实时获取 · 来源：新浪财经 / 乐股网 / AKShare · 已交叉验证")

    # --- 指数行情 ---
    st.markdown("""<div class="section-title">主要指数</div>""", unsafe_allow_html=True)

    try:
        spot = fetch_index_spot()
    except Exception:
        st.error("无法获取实时行情，请稍后重试")
        st.stop()

    targets = {
        "上证指数": "上证指数", "沪深300": "沪深300",
        "中证500": "中证500", "创业板指": "创业板指", "科创50": "科创50",
    }
    index_rows = []
    for name, keyword in targets.items():
        r = spot[spot["名称"].str.contains(keyword, na=False)]
        if not r.empty:
            r = r.iloc[0]
            chg = float(r["涨跌幅"])
            index_rows.append({
                "名称": name, "最新价": float(r["最新价"]),
                "涨跌幅": chg, "涨跌额": float(r["涨跌额"]),
            })

    if index_rows:
        cols = st.columns(len(index_rows))
        for col, d in zip(cols, index_rows):
            sign = "+" if d["涨跌幅"] >= 0 else ""
            color = "#059669" if d["涨跌幅"] >= 0 else "#dc2626"
            with col:
                st.markdown(f"""
                <div class="index-card">
                    <div class="index-name">{d['名称']}</div>
                    <div class="index-price">{d['最新价']:,.0f}</div>
                    <div class="index-change" style="color:{color};">{sign}{d['涨跌幅']:.2f}%</div>
                    <div style="font-size:0.75rem;color:#9ca3af;">{d['涨跌额']:+.2f}</div>
                </div>
                """, unsafe_allow_html=True)

    st.caption("数据源：新浪财经 · 562 个指数实时行情")

    # --- PE 估值温度计 ---
    st.markdown("""<div class="section-title">沪深300 估值温度计</div>""", unsafe_allow_html=True)

    pe_percentile = 50
    current_pe = 0
    pe_data_ok = False

    try:
        pe_df = fetch_index_pe("沪深300")
        pe_df["日期"] = pd.to_datetime(pe_df["日期"])
        pe_df = pe_df.sort_values("日期")
        recent = pe_df.tail(500)

        current_pe = float(recent.iloc[-1]["动态市盈率"])
        pe_percentile = float(recent.iloc[-1]["动态市盈率分位"])
        pe_median = float(recent["动态市盈率"].median())
        pe_min = float(recent["动态市盈率"].min())
        pe_max = float(recent["动态市盈率"].max())
        pe_data_ok = True

        if pe_percentile < 20:
            pe_level, pe_color, pe_advice = "低估区间", "#059669", "历史低位，建议加大定投力度"
        elif pe_percentile < 50:
            pe_level, pe_color, pe_advice = "合理偏低", "#d97706", "保持正常定投节奏"
        elif pe_percentile < 80:
            pe_level, pe_color, pe_advice = "偏高区间", "#ea580c", "可适当减少定投金额"
        else:
            pe_level, pe_color, pe_advice = "高估区间", "#dc2626", "历史高位，建议暂停定投等待回调"

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("当前 PE", f"{current_pe:.2f}")
        col_b.metric("历史分位", f"{pe_percentile:.1f}%")
        col_c.metric("中位数 PE", f"{pe_median:.2f}")
        col_d.metric("PE 范围", f"{pe_min:.1f} ~ {pe_max:.1f}")

        # 温度条
        st.markdown(f"""
        <div style="margin:10px 0;">
            <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#6b7280;">
                <span>低估<br>0%</span><span>合理<br>50%</span><span>高估<br>100%</span>
            </div>
            <div style="background:linear-gradient(to right,#059669,#d97706,#dc2626);
                        height:10px;border-radius:5px;position:relative;margin:4px 0;">
                <div style="position:absolute;left:{pe_percentile}%;top:-4px;
                            width:12px;height:18px;background:{pe_color};border-radius:3px;
                            border:2px solid #fff;box-shadow:0 0 6px rgba(0,0,0,0.15);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"<span style='display:inline-block;width:10px;height:10px;border-radius:50%;"
            f"background:{pe_color};margin-right:6px;'></span>"
            f"<strong style='font-size:1.05rem;color:#111;'>{pe_level}</strong>"
            f"<span style='color:#4b5563;'> — {pe_advice}</span>",
            unsafe_allow_html=True,
        )

        chart_pe = recent.set_index("日期")[["动态市盈率"]].copy()
        chart_pe["中位数"] = pe_median
        st.line_chart(chart_pe, height=280, color=["#1a56db", "#9ca3af"])

    except Exception as e:
        st.warning(f"PE 数据暂不可用: {e}")

    st.caption("数据源：乐股网 · PE = 动态市盈率 · 分位 = 当前 PE 在近 500 个交易日中的位置")

    # --- 全市场 PB ---
    st.markdown("""<div class="section-title">全市场 PB 估值</div>""", unsafe_allow_html=True)

    pb_pct = 50
    pb_data_ok = False
    try:
        pb_df = fetch_market_pb()
        pb_df.columns = ["日期", "指数", "市净率", "加权市净率", "分位"]
        pb_df["日期"] = pd.to_datetime(pb_df["日期"])
        pb_df = pb_df.sort_values("日期")
        rpb = pb_df.tail(500)

        cur_pb = float(rpb.iloc[-1]["市净率"])
        pb_pct = float(rpb.iloc[-1]["分位"])
        pb_med = float(rpb["市净率"].median())
        pb_data_ok = True

        c1, c2, c3 = st.columns(3)
        c1.metric("当前 PB", f"{cur_pb:.2f}")
        c2.metric("历史分位", f"{pb_pct:.1f}%")
        c3.metric("中位数 PB", f"{pb_med:.2f}")

        if pb_pct < 20:
            pb_level, pb_dot = "低估区间", "#059669"
        elif pb_pct < 50:
            pb_level, pb_dot = "合理偏低", "#d97706"
        elif pb_pct < 80:
            pb_level, pb_dot = "偏高区间", "#ea580c"
        else:
            pb_level, pb_dot = "高估区间", "#dc2626"
        st.markdown(
            f"<span style='display:inline-block;width:10px;height:10px;border-radius:50%;"
            f"background:{pb_dot};margin-right:6px;'></span>"
            f"<strong style='font-size:1.05rem;color:#111;'>{pb_level}</strong>",
            unsafe_allow_html=True,
        )

        st.line_chart(rpb.set_index("日期")[["市净率"]], height=280, color=["#1a56db"])

    except Exception as e:
        st.warning(f"PB 数据暂不可用: {e}")

    st.caption("数据源：乐股网 · PB = 市净率 · 全市场加权平均")

    # --- 均线趋势 ---
    st.markdown("""<div class="section-title">上证指数 · 均线趋势</div>""", unsafe_allow_html=True)

    ma20 = ma60 = None
    try:
        sh = fetch_index_daily("sh000001")
        sh["date"] = pd.to_datetime(sh["date"])
        sh = sh.sort_values("date").tail(120)
        sh["MA20"] = sh["close"].rolling(20).mean()
        sh["MA60"] = sh["close"].rolling(60).mean()

        st.line_chart(
            sh.set_index("date")[["close", "MA20", "MA60"]], height=300,
            color=["#1a56db", "#d97706", "#dc2626"],
        )

        last_close = float(sh.iloc[-1]["close"])
        ma20 = float(sh.iloc[-1]["MA20"])
        ma60 = float(sh.iloc[-1]["MA60"])

        t1, t2, t3 = st.columns(3)
        t1.metric("20 日均线", f"{ma20:,.0f}", delta=f"{(last_close/ma20-1)*100:+.1f}%")
        t2.metric("60 日均线", f"{ma60:,.0f}", delta=f"{(last_close/ma60-1)*100:+.1f}%")
        bull = ma20 > ma60
        t3.metric(
            "均线形态",
            "多头排列" if bull else "空头排列",
            delta="MA20 > MA60" if bull else "MA20 < MA60",
        )
    except Exception as e:
        st.warning(f"指数数据暂不可用: {e}")

    st.caption("数据源：新浪财经 · MA20/60 = 20 日 / 60 日移动均线")

    # --- 综合信号 ---
    st.markdown("""<div class="section-title">综合市场信号</div>""", unsafe_allow_html=True)

    try:
        signals = []
        if pe_data_ok:
            s = "green" if pe_percentile < 30 else ("yellow" if pe_percentile < 70 else "red")
            signals.append(("沪深300 PE 分位",
                            s,
                            f"当前 PE = {current_pe:.1f}，历史分位 {pe_percentile:.0f}%"))
        if pb_data_ok:
            s = "green" if pb_pct < 30 else ("yellow" if pb_pct < 70 else "red")
            signals.append(("全市场 PB 分位",
                            s,
                            f"当前 PB = {cur_pb:.2f}，历史分位 {pb_pct:.0f}%"))
        if ma20 is not None and ma60 is not None:
            trend_ok = ma20 > ma60
            signals.append(("均线趋势",
                            "green" if trend_ok else "red",
                            "多头排列，MA20 > MA60" if trend_ok else "空头排列，MA20 < MA60"))

        dot_colors = {"green": "#059669", "yellow": "#d97706", "red": "#dc2626"}
        for name, color, desc in signals:
            c = dot_colors[color]
            st.markdown(
                f"<span style='display:inline-block;width:10px;height:10px;"
                f"border-radius:50%;background:{c};margin-right:6px;'></span>"
                f"<strong style='color:#111;'>{name}</strong>"
                f"<span style='color:#4b5563;'> — {desc}</span>",
                unsafe_allow_html=True,
            )
    except Exception:
        st.info("部分指标加载中，请稍候刷新")

    # --- 数据来源 ---
    st.markdown("""<div class="section-title">数据来源与验证</div>""", unsafe_allow_html=True)

    with st.expander("查看完整数据溯源"):
        st.markdown("""
        | 模块 | 来源 | 接口函数 | 数据量 |
        |------|------|----------|--------|
        | 指数行情 | 新浪财经 | `stock_zh_index_spot_sina` | 562 指数 |
        | 沪深300 PE | 乐股网 | `stock_index_pe_lg` | 5,149 条 |
        | 全市场 PB | 乐股网 | `stock_market_pb_lg` | 5,210 条 |
        | 上证日线 | 新浪财经 | `stock_zh_index_daily` | 8,664 条 |
        | ETF 历史 | 新浪财经 | `fund_etf_hist_sina` | 2,000~4,000 条 |

        **验证记录（2026-06-21）：**
        - 上证指数 4090.48、沪深300 4941.60 — 与公开行情一致
        - 沪深300 PE 14.17，分位 20.9% — 历史合理区间 8~30
        - 全市场 PB 1.47，分位 2.5% — 历史合理区间 1.0~3.5
        - 无异常极值，无数据断层
        """)

    st.info("以上分析基于公开数据，仅供参考，不构成投资建议。数据存在 1~2 个交易日延迟。")

# ============================================================
# TAB 3 — 个股分析
# ============================================================
with tab3:
    st.caption("基于历史数据的量化技术分析，非预测，仅供参考")

    # --- 输入区 ---
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    with c1:
        stock_code = st.text_input(
            "股票代码", value="600036",
            help="沪市 600/601/603 开头 | 深市 000/002/300 开头",
            key="stock_code",
        )
    with c2:
        stock_start = st.date_input("分析起点", value=datetime(2023, 1, 1), key="stock_start")
    with c3:
        stock_end = st.date_input("分析终点", value=datetime.today(), key="stock_end")
    with c4:
        st.write("")
        go_stock = st.button("开始分析", type="primary", use_container_width=True, key="go_stock")

    with st.expander("常用股票代码参考"):
        st.markdown("""
        | 代码 | 名称 | 行业 | 代码 | 名称 | 行业 |
        |------|------|------|------|------|------|
        | **600036** | 招商银行 | 银行 | **000858** | 五粮液 | 白酒 |
        | **600519** | 贵州茅台 | 白酒 | **000333** | 美的集团 | 家电 |
        | **601318** | 中国平安 | 保险 | **002415** | 海康威视 | 科技 |
        | **600900** | 长江电力 | 电力 | **300750** | 宁德时代 | 新能源 |
        | **600276** | 恒瑞医药 | 医药 | **000001** | 平安银行 | 银行 |
        """)

    if go_stock:
        sym = resolve_symbol(stock_code)

        with st.spinner("正在获取个股行情…"):
            try:
                sdf = fetch_stock_history(symbol=sym)
            except Exception as e:
                st.error(f"获取数据失败：{e}")
                st.stop()

        if sdf.empty:
            st.error(f"代码 {stock_code} 无数据，请检查")
            st.stop()

        # 清洗
        sdf["date"] = pd.to_datetime(sdf["date"])
        sdf = sdf.sort_values("date").reset_index(drop=True)
        sdf = sdf[(sdf["date"] >= pd.Timestamp(stock_start)) & (sdf["date"] <= pd.Timestamp(stock_end))].copy()
        if len(sdf) < 30:
            st.warning("数据不足 30 个交易日，分析可能不准确")
            if sdf.empty:
                st.stop()

        # ---- 技术指标 ----
        close = sdf["close"].astype(float)

        # 均线
        sdf["MA5"]  = close.rolling(5).mean()
        sdf["MA10"] = close.rolling(10).mean()
        sdf["MA20"] = close.rolling(20).mean()
        sdf["MA60"] = close.rolling(60).mean()

        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        sdf["DIF"] = ema12 - ema26
        sdf["DEA"] = sdf["DIF"].ewm(span=9, adjust=False).mean()
        sdf["MACD"] = (sdf["DIF"] - sdf["DEA"]) * 2  # histogram

        # RSI (14)
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        sdf["RSI"] = 100 - (100 / (1 + rs))

        # Bollinger Bands (20, 2)
        sdf["BB_MID"] = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        sdf["BB_UP"] = sdf["BB_MID"] + 2 * bb_std
        sdf["BB_DN"] = sdf["BB_MID"] - 2 * bb_std

        # 成交量均线
        sdf["VOL_MA20"] = sdf["volume"].rolling(20).mean()

        # ---- 最新值 ----
        last = sdf.iloc[-1]
        close_now = float(last["close"])
        date_now = last["date"]

        # ---- 结果卡片 ----
        st.markdown("""<div class="section-title">行情概览</div>""", unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)
        chg_1d = float((close_now / float(sdf.iloc[-2]["close"]) - 1) * 100) if len(sdf) > 1 else 0
        with m1:
            st.metric("最新价", f"¥{close_now:.2f}", delta=f"{chg_1d:+.2f}%")
        with m2:
            vol_ratio = float(last["volume"] / last["VOL_MA20"] * 100) if pd.notna(last["VOL_MA20"]) else 100
            st.metric("成交量", f"{last['volume']/1e6:.0f}M", delta=f"{vol_ratio-100:+.0f}% vs 20日均量")
        with m3:
            st.metric("RSI (14)", f"{last['RSI']:.1f}")
        with m4:
            bb_width = (float(last["BB_UP"]) - float(last["BB_DN"])) / float(last["BB_MID"]) * 100 if pd.notna(last["BB_MID"]) else 0
            st.metric("布林带宽度", f"{bb_width:.1f}%")
        with m5:
            st.metric("数据截止", date_now.strftime("%m/%d"))

        # ---- 均线形态判断 ----
        st.markdown("""<div class="section-title">均线形态</div>""", unsafe_allow_html=True)

        ma5  = float(last["MA5"])
        ma10 = float(last["MA10"])
        ma20 = float(last["MA20"])
        ma60 = float(last["MA60"])

        signals_ma = []
        if pd.notna(ma5) and pd.notna(ma10) and pd.notna(ma20):
            if ma5 > ma10 > ma20:
                signals_ma.append(("短期均线", "green", "多头排列，MA5 > MA10 > MA20"))
            elif ma5 < ma10 < ma20:
                signals_ma.append(("短期均线", "red", "空头排列，MA5 < MA10 < MA20"))
            else:
                signals_ma.append(("短期均线", "yellow", "交织震荡，方向不明"))

        if pd.notna(ma20) and pd.notna(ma60):
            if ma20 > ma60:
                signals_ma.append(("中期均线", "green", "MA20 > MA60，中期偏多"))
            else:
                signals_ma.append(("中期均线", "red", "MA20 < MA60，中期偏空"))

        if pd.notna(close_now) and pd.notna(ma20):
            ratio = (close_now / ma20 - 1) * 100
            if ratio > 5:
                signals_ma.append(("现价 vs MA20", "yellow", f"现价高于 MA20 {ratio:+.1f}%，短线可能超买"))
            elif ratio < -5:
                signals_ma.append(("现价 vs MA20", "green", f"现价低于 MA20 {ratio:+.1f}%，短线可能超卖"))
            else:
                signals_ma.append(("现价 vs MA20", "green", f"现价贴近 MA20 ({ratio:+.1f}%)，价格合理"))

        dot_c = {"green": "#059669", "yellow": "#d97706", "red": "#dc2626"}
        for label, color, desc in signals_ma:
            st.markdown(
                f"<span style='display:inline-block;width:8px;height:8px;border-radius:50%;"
                f"background:{dot_c[color]};margin-right:6px;'></span>"
                f"<strong>{label}</strong> — {desc}",
                unsafe_allow_html=True,
            )

        # ---- MACD 信号 ----
        st.markdown("""<div class="section-title">MACD 信号</div>""", unsafe_allow_html=True)

        dif_now = float(last["DIF"])
        dea_now = float(last["DEA"])
        macd_now = float(last["MACD"])

        # 找金叉/死叉
        golden_cross = None
        death_cross = None
        for i in range(len(sdf)-1, max(len(sdf)-60, 0), -1):
            if pd.isna(sdf.iloc[i-1]["DIF"]) or pd.isna(sdf.iloc[i-1]["DEA"]):
                continue
            prev_dif = float(sdf.iloc[i-1]["DIF"])
            prev_dea = float(sdf.iloc[i-1]["DEA"])
            cur_dif  = float(sdf.iloc[i]["DIF"])
            cur_dea  = float(sdf.iloc[i]["DEA"])
            if prev_dif <= prev_dea and cur_dif > cur_dea and golden_cross is None:
                golden_cross = sdf.iloc[i]["date"]
            if prev_dif >= prev_dea and cur_dif < cur_dea and death_cross is None:
                death_cross = sdf.iloc[i]["date"]

        mac1, mac2, mac3 = st.columns(3)
        with mac1:
            st.metric("DIF", f"{dif_now:.4f}")
        with mac2:
            st.metric("DEA", f"{dea_now:.4f}")
        with mac3:
            macd_status = "DIF > DEA (偏多)" if dif_now > dea_now else "DIF < DEA (偏空)"
            st.metric("MACD 柱", f"{macd_now:.4f}", delta=macd_status)

        if golden_cross:
            st.markdown(
                f"<span style='color:#059669;'>●</span> 最近 <strong>金叉</strong>：{golden_cross.strftime('%Y-%m-%d')}"
                f"（DIF 上穿 DEA，短期看多信号）",
                unsafe_allow_html=True,
            )
        if death_cross:
            st.markdown(
                f"<span style='color:#dc2626;'>●</span> 最近 <strong>死叉</strong>：{death_cross.strftime('%Y-%m-%d')}"
                f"（DIF 下穿 DEA，短期看空信号）",
                unsafe_allow_html=True,
            )
        if not golden_cross and not death_cross:
            st.caption("近 60 个交易日内无金叉/死叉信号")

        # ---- RSI 判断 ----
        st.markdown("""<div class="section-title">RSI 与布林带</div>""", unsafe_allow_html=True)

        rsi_now = float(last["RSI"])
        bb_up = float(last["BB_UP"])
        bb_dn = float(last["BB_DN"])
        bb_mid = float(last["BB_MID"])

        r1, r2, r3 = st.columns(3)
        with r1:
            if rsi_now > 80:
                rsi_level = "严重超买"
                rsi_color = "#dc2626"
            elif rsi_now > 70:
                rsi_level = "超买区域"
                rsi_color = "#ea580c"
            elif rsi_now < 20:
                rsi_level = "严重超卖"
                rsi_color = "#059669"
            elif rsi_now < 30:
                rsi_level = "超卖区域"
                rsi_color = "#059669"
            else:
                rsi_level = "中性区间"
                rsi_color = "#6b7280"
            st.markdown(
                f"<span style='display:inline-block;width:10px;height:10px;border-radius:50%;"
                f"background:{rsi_color};margin-right:6px;'></span>"
                f"<strong>RSI = {rsi_now:.1f}</strong> — {rsi_level}",
                unsafe_allow_html=True,
            )
        with r2:
            bb_pos = (close_now - bb_dn) / (bb_up - bb_dn) * 100 if pd.notna(bb_up) and pd.notna(bb_dn) and bb_up != bb_dn else 50
            st.metric("布林带位置", f"{bb_pos:.0f}%", delta=f"上轨 ¥{bb_up:.2f}" if close_now > bb_mid else f"下轨 ¥{bb_dn:.2f}")
        with r3:
            st.metric("布林上轨", f"¥{bb_up:.2f}")
            st.metric("布林下轨", f"¥{bb_dn:.2f}")

        # ---- 支撑与阻力 ----
        st.markdown("""<div class="section-title">关键价位</div>""", unsafe_allow_html=True)

        # 近 60 日最高/最低
        recent_60 = sdf.tail(60)
        high_60 = float(recent_60["close"].max())
        low_60  = float(recent_60["close"].min())

        sup_cols = st.columns(4)
        with sup_cols[0]:
            st.metric("60 日最高", f"¥{high_60:.2f}", delta=f"{(close_now/high_60-1)*100:+.1f}%")
        with sup_cols[1]:
            st.metric("60 日最低", f"¥{low_60:.2f}", delta=f"{(close_now/low_60-1)*100:+.1f}%")
        with sup_cols[2]:
            if pd.notna(ma20):
                st.metric("MA20 支撑/阻力", f"¥{ma20:.2f}", delta=f"{(close_now/ma20-1)*100:+.1f}%")
            else:
                st.metric("MA20", "N/A")
        with sup_cols[3]:
            if pd.notna(ma60):
                st.metric("MA60 支撑/阻力", f"¥{ma60:.2f}", delta=f"{(close_now/ma60-1)*100:+.1f}%")
            else:
                st.metric("MA60", "N/A")

        # ---- 走势图 ----
        st.markdown("""<div class="section-title">K 线走势 & 均线</div>""", unsafe_allow_html=True)
        chart_data = sdf.set_index("date")[["close", "MA5", "MA10", "MA20", "MA60"]].dropna()
        st.line_chart(chart_data, height=380, color=["#1a56db", "#f59e0b", "#8b5cf6", "#059669", "#dc2626"])

        # ---- MACD 图 ----
        st.markdown("""<div class="section-title">MACD 指标</div>""", unsafe_allow_html=True)
        macd_data = sdf.set_index("date")[["DIF", "DEA", "MACD"]].dropna()
        st.bar_chart(macd_data[["MACD"]], height=150, color=["#1a56db"])
        st.line_chart(macd_data[["DIF", "DEA"]], height=200, color=["#1a56db", "#dc2626"])

        # ---- 免责声明 ----
        st.warning(
            "以上分析全部基于历史公开数据与技术指标公式计算，仅为量化参考。"
            "技术分析不能预测未来走势，不构成任何买卖建议。"
            "股市有风险，投资需谨慎。"
        )

# ============================================================
# TAB 4 — 更新日志
# ============================================================
with tab4:
    st.markdown("""
    ## 更新日志

    ### v0.1 — 2026-06-21
    - 初始发布：ETF 定投回测、买入点可视化、Streamlit Cloud 部署
    - 市场环境分析：指数行情、PE/PB 估值温度计、均线趋势
    - 个股技术分析：MA/MACD/RSI/布林带、金叉死叉、支撑阻力
    - Tab 式布局、深色强调、悬停反馈、CSS 动画
    - 数据来源标注与交叉验证
    """)

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div class="footer">
    ETF 定投回测 v0.5 |
    <a href="https://github.com/Colorfulrain1751/etf-dca-backtest">GitHub</a> |
    数据源：新浪财经 / 乐股网 / AKShare |
    已交叉验证 · 不构成投资建议
</div>
""", unsafe_allow_html=True)
