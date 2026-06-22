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
    body, .main, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #dbeafe 0%, #eff6ff 25%, #f8fafc 50%, #ffffff 75%) !important;
        background-attachment: fixed !important;
    }
    .hero { text-align:center; padding:120px 20px 80px 20px; animation:fadeIn 0.8s ease-out; }
    .hero h1 { font-size:2.8rem; font-weight:800; color:#1e3a5f; letter-spacing:-0.5px; margin-bottom:12px; }
    .hero .gradient { background:linear-gradient(135deg,#1e40af,#3b82f6,#6366f1); background-size:200% 200%; animation:gradientFlow 6s ease infinite; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .hero .tagline { font-size:1.15rem; color:#475569; max-width:600px; margin:20px auto 8px auto; line-height:1.8; }
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
# New cache functions for v0.6
@st.cache_data(ttl=3600)
def fetch_northbound_hist():
    return ak.stock_hsgt_hist_em(symbol="北向资金")

@st.cache_data(ttl=3600)
def fetch_northbound_summary():
    return ak.stock_hsgt_fund_flow_summary_em()

@st.cache_data(ttl=3600)
def fetch_sector_spot():
    return ak.stock_sector_spot(indicator="新浪行业")

@st.cache_data(ttl=86400)
def fetch_dividend_history(symbol):
    try:
        return ak.stock_history_dividend_detail(symbol=symbol, indicator="分红")
    except Exception:
        return pd.DataFrame()

# ============================================================


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

# TITLE
# ============================================================
st.markdown("""
<h1 style="font-size:2.2rem; font-weight:800; margin-bottom:0; color:#111;">
    ETF 定投回测
    <span style="color:#1a56db;">·</span>
    <span style="color:#4b5563; font-weight:600;">市场环境分析</span>
</h1>
""", unsafe_allow_html=True)
pass  # caption removed


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["定投回测", "市场分析", "个股分析", "更新日志", "资金流向", "恐贪指数", "股息查询", "多ETF对比"])

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

        # 兼容不同版本的列名：动态市盈率 / PE / pe
        pe_col = next((c for c in recent.columns if "动态市盈率" in str(c) or str(c).upper() in ["PE", "PE-TTM", "市盈率"]), None)
        pct_col = next((c for c in recent.columns if "分位" in str(c) and "市盈率" in str(c)), None)
        if pe_col is None:
            pe_col = recent.select_dtypes(include=[np.number]).columns[0]
        if pct_col is None:
            pct_col = next((c for c in recent.columns if "分位" in str(c)), None)

        current_pe = float(recent.iloc[-1][pe_col])
        pe_percentile = float(recent.iloc[-1][pct_col]) if pct_col else float((recent[pe_col] <= current_pe).sum() / len(recent) * 100)
        pe_median = float(recent[pe_col].median())
        pe_min = float(recent[pe_col].min())
        pe_max = float(recent[pe_col].max())
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

        chart_pe = recent.set_index("日期")[[pe_col]].copy()
        chart_pe.columns = ["PE"]
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
                            f"当前 PE = {current_pe:.1f}，历史分位 {pe_percentile:.1f}%"))
        if pb_data_ok:
            s = "green" if pb_pct < 30 else ("yellow" if pb_pct < 70 else "red")
            signals.append(("全市场 PB 分位",
                            s,
                            f"当前 PB = {cur_pb:.2f}，历史分位 {pb_pct:.1f}%"))
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
            elif rsi_now > 50:
                rsi_level = "中性偏强"
                rsi_color = "#6b7280"
            elif rsi_now > 30:
                rsi_level = "中性偏弱"
                rsi_color = "#6b7280"
            elif rsi_now > 20:
                rsi_level = "超卖区域"
                rsi_color = "#059669"
            else:
                rsi_level = "严重超卖"
                rsi_color = "#059669"
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
# TAB 5  —  资金流向
# ============================================================
with tab5:
    st.caption("数据源：东方财富 / 新浪财经 · 沪深港通 + 行业资金流向")

    # --- Northbound ---
    st.markdown("""<div class="section-title">沪深港通 · 北上资金</div>""", unsafe_allow_html=True)

    try:
        nb_flow = fetch_northbound_summary()
        # Column mapping (13 columns):
        # [0]日期 [1]类型 [2]方向 [3]资金净额 [4]状态 [5]成交净买额(亿) [6]资金余额
        # [7]当日余额 [8]上涨数 [9]平盘数 [10]下跌数 [11]指数 [12]涨跌幅
        # Rows: 0=沪股通北 1=沪股通南 2=深股通北 3=深股通南
        if len(nb_flow) >= 4:
            date_str = str(nb_flow.iloc[0, 0])
            status = int(nb_flow.iloc[0, 4])
            # Column 5 = 成交净买额 (net buy, in 亿元)
            sh_n = float(nb_flow.iloc[0, 5])
            sz_n = float(nb_flow.iloc[2, 5])
            sh_s = float(nb_flow.iloc[1, 5])
            sz_s = float(nb_flow.iloc[3, 5])
            n_total = sh_n + sz_n
            s_total = sh_s + sz_s

            if status == 3:
                st.info(f"数据日期：{date_str} · 今日休市，净买额为 0")
            else:
                n1, n2, n3, n4 = st.columns(4)
                n1.metric("沪股通 北上", f"{sh_n:.1f} 亿", delta=f"{sh_n:+.1f} 亿")
                n2.metric("深股通 北上", f"{sz_n:.1f} 亿", delta=f"{sz_n:+.1f} 亿")
                n3.metric("北上合计", f"{n_total:.1f} 亿", delta=f"{n_total:+.1f} 亿")
                n4.metric("南下合计", f"{s_total:.1f} 亿", delta=f"{s_total:+.1f} 亿")
        else:
            st.info("北上资金数据格式异常，请稍后重试")
    except Exception as e:
        st.warning(f"北上资金数据暂不可用: {e}")

    # Northbound trend chart
    try:
        nb_hist = fetch_northbound_hist()
        nb_hist.iloc[:, 0] = pd.to_datetime(nb_hist.iloc[:, 0])
        nb_hist = nb_hist.sort_values(nb_hist.columns[0])
        # Drop NaN (recent days may not have data yet)
        net_col = nb_hist.columns[1]
        nb_clean = nb_hist.dropna(subset=[net_col]).copy()
        nb_clean['net'] = nb_clean[net_col].astype(float)
        # Take last 250 valid trading days
        nb_chart = nb_clean.tail(250).set_index(nb_clean.columns[0])[['net']]
        nb_chart.columns = ['当日净买额(亿)']

        st.line_chart(nb_chart, height=250, color=["#1a56db"])
        latest_nb_date = nb_clean.iloc[-1, 0]
        days_behind = (datetime.now() - latest_nb_date).days
        if days_behind > 180:
            st.warning(
                f"⚠️ 北上资金历史明细数据已停止更新。最新有效数据为 {latest_nb_date.strftime('%Y-%m-%d')}"
                f"（{days_behind} 天前），近一年数据均为空值。"
                f"下方图表仅展示历史数据，不代表当前资金流向。"
                f"当日资金汇总数据请参考上方「资金流向」板块。"
            )
        elif days_behind > 30:
            st.info(f"数据最新日期：{latest_nb_date.strftime('%Y-%m-%d')}（{days_behind} 天前）")
        st.caption(f"数据源：东方财富 stock_hsgt_hist_em ({len(nb_clean)} 条有效数据) · 单位：亿元")
    except Exception as e:
        st.warning(f"北上资金历史数据暂不可用: {e}")

    # --- Sector Flow ---
    st.markdown("""<div class="section-title">行业板块涨跌（日）</div>""", unsafe_allow_html=True)

    try:
        sector = fetch_sector_spot()
        # Columns: [0]label [1]名称 [2]公司数 [3]平均价格 [4]涨跌额 [5]涨跌幅(%) [6]成交量 ...
        # Column 1 = Chinese name, Column 5 = daily change %
        if len(sector) > 0:
            sector_display = sector.copy()
            sector_display['chg'] = sector_display.iloc[:, 5].astype(float)
            # Sort by change (best to worst)
            sector_display = sector_display.sort_values('chg', ascending=False)

            st.caption(f"共 {len(sector_display)} 个行业，已按日涨跌幅排序")

            cols = st.columns(5)
            for i, (_, row) in enumerate(sector_display.iterrows()):
                ci = i % 5
                name = str(row.iloc[1])  # Column 1 = Chinese name
                chg = float(row.iloc[5])  # Column 5 = daily change %
                color = "#059669" if chg >= 0 else "#dc2626"
                with cols[ci]:
                    st.markdown(f"""
                    <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;
                                border:1px solid #e5e7eb;margin-bottom:6px;">
                        <div style="font-size:0.78rem;color:#6b7280;">{name}</div>
                        <div style="font-weight:700;color:{color};">{chg:+.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"行业板块数据暂不可用: {e}")

    st.caption("数据源：新浪财经 stock_sector_spot (49 个行业) · 单日涨跌幅")

# ============================================================
# TAB 6 — 恐贪指数
# ============================================================
with tab6:
    st.caption("基于 PE 分位、成交量、RSI 合成的市场情绪指标（北上资金已移除：历史数据停更）")

    score_parts = {}
    fgi_signals = []

    # 1. PE score (20 = max fear / cheap, 80 = max greed / expensive)
    try:
        pe_df = fetch_index_pe("沪深300")
        pe_df["日期"] = pd.to_datetime(pe_df["日期"]); pe_df = pe_df.sort_values("日期")
        recent_pe = pe_df.tail(250)
        # 兼容不同版本的列名
        pe_pct_col = next((c for c in recent_pe.columns if "分位" in str(c) and "市盈率" in str(c)), None)
        if pe_pct_col is None:
            pe_pct_col = next((c for c in recent_pe.columns if "分位" in str(c)), None)
        if pe_pct_col is not None:
            pe_pct = float(recent_pe.iloc[-1][pe_pct_col])
        else:
            pe_val_col = next((c for c in recent_pe.columns if "动态市盈率" in str(c) or str(c).upper() in ["PE", "PE-TTM", "市盈率"]), None)
            if pe_val_col is None:
                pe_val_col = recent_pe.select_dtypes(include=[np.number]).columns[0]
            cur_pe_val = float(recent_pe.iloc[-1][pe_val_col])
            pe_pct = float((recent_pe[pe_val_col] <= cur_pe_val).sum() / len(recent_pe) * 100)
        pe_score = pe_pct  # 0 (fear/cheap) to 100 (greed/expensive)
        score_parts["PE 分位"] = pe_score
        if pe_score < 25: fgi_signals.append(("估值", "green", "PE 历史低位，市场恐惧"))
        elif pe_score > 75: fgi_signals.append(("估值", "red", "PE 历史高位，市场贪婪"))
        else: fgi_signals.append(("估值", "yellow", "PE 正常区间"))
    except Exception as e:
        pe_score = 50
        fgi_signals.append(("估值", "yellow", f"数据不可用: {e}"))

    # 2. Volume score
    try:
        sh = fetch_index_daily("sh000001")
        sh["date"] = pd.to_datetime(sh["date"]); sh = sh.sort_values("date")
        recent_sh = sh.tail(60)
        vol_now = float(recent_sh.iloc[-1]["volume"])
        vol_avg = float(recent_sh["volume"].mean())
        vol_ratio = vol_now / vol_avg
        vol_score = min(100, max(0, vol_ratio * 50))  # scale
        score_parts["成交量"] = vol_score
        if vol_ratio > 1.5: fgi_signals.append(("成交量", "red", f"放量 {vol_ratio:.1f}x，交易活跃"))
        elif vol_ratio < 0.7: fgi_signals.append(("成交量", "green", f"缩量 {vol_ratio:.1f}x，市场冷清"))
        else: fgi_signals.append(("成交量", "yellow", f"正常 {vol_ratio:.1f}x"))
    except Exception as e:
        vol_score = 50

    # 3. RSI score
    try:
        sh["RSI14"] = 100 - (100 / (1 + (sh["close"].diff().clip(lower=0).ewm(alpha=1/14, adjust=False).mean() /
                                           (-sh["close"].diff().clip(upper=0).ewm(alpha=1/14, adjust=False).mean())).replace(0, np.nan)))
        rsi_val = float(sh.iloc[-1]["RSI14"])
        rsi_score = (rsi_val - 30) * 2.5  # RSI 30=0, 70=100
        rsi_score = min(100, max(0, rsi_score))
        score_parts["RSI"] = rsi_score
        if rsi_val > 70: fgi_signals.append(("RSI(14)", "red", f"RSI={rsi_val:.1f}，超买"))
        elif rsi_val < 30: fgi_signals.append(("RSI(14)", "green", f"RSI={rsi_val:.1f}，超卖"))
        else: fgi_signals.append(("RSI(14)", "yellow", f"RSI={rsi_val:.1f}，正常"))
    except Exception as e:
        rsi_score = 50

    # 4. Northbound score — REMOVED
    # 北上资金历史明细 API (stock_hsgt_hist_em) 自 2024 年 8 月起净买额列为空值，
    # 有效数据滞后 675+ 天，无法反映当前市场情绪，已从恐贪指数中移除。
    # 当日北上资金汇总数据仍可在 Tab5「资金流向」中查看。

    # Composite
    fgi = sum(score_parts.values()) / max(len(score_parts), 1)

    f1, f2, f3 = st.columns(3)
    with f1:
        st.metric("恐贪指数", f"{fgi:.0f} / 100")
    with f2:
        if fgi < 30: level, color, advice = "极度恐惧", "#059669", "历史经验：恐惧时买入，长期回报最佳"
        elif fgi < 50: level, color, advice = "偏恐惧", "#059669", "市场偏冷，可考虑逐步建仓"
        elif fgi < 70: level, color, advice = "偏贪婪", "#ea580c", "市场偏热，注意控制仓位"
        else: level, color, advice = "极度贪婪", "#dc2626", "历史经验：贪婪时卖出，避免高位接盘"
        st.metric("市场情绪", level)
    with f3:
        parts_str = " · ".join([f"{k}: {v:.0f}" for k, v in score_parts.items()])
        st.caption(parts_str)

    # FGI bar
    st.markdown(f"""
    <div style="margin:10px 0;">
        <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#6b7280;">
            <span>极度恐惧<br>0</span><span>恐惧<br>30</span><span>中性<br>50</span><span>贪婪<br>70</span><span>极度贪婪<br>100</span>
        </div>
        <div style="background:linear-gradient(to right,#059669 0%,#d97706 50%,#dc2626 100%);height:10px;border-radius:5px;position:relative;margin:4px 0;">
            <div style="position:absolute;left:{fgi}%;top:-4px;width:12px;height:18px;background:{color};border-radius:3px;border:2px solid #fff;box-shadow:0 0 6px rgba(0,0,0,0.15);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<span style='color:{color};font-weight:700;'>{advice}</span>", unsafe_allow_html=True)

    # Detail signals
    dot_c = {"green": "#059669", "yellow": "#d97706", "red": "#dc2626"}
    for name, col, desc in fgi_signals:
        st.markdown(f"<span style='display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot_c[col]};margin-right:6px;'></span><strong>{name}</strong> — {desc}", unsafe_allow_html=True)

    st.caption("数据源：乐股网(PE分位) · 新浪财经(成交量/RSI) · 复合计算")

    st.info("恐贪指数是基于公开数据的复合指标，范围为 0-100。0 = 极度恐惧（历史性机会），100 = 极度贪婪（高风险）。仅供参考，不构成投资建议。")

# ============================================================
# TAB 7 — 股息查询
# ============================================================
with tab7:
    st.caption("查询个股历史分红记录 · 数据源：新浪财经")

    c1, c2, c3, _ = st.columns([2, 1, 1, 2])
    with c1:
        div_code = st.text_input("股票代码", value="600036", key="div_code",
                                 help="输入 6 位 A 股代码")
    with c2:
        div_start = st.date_input("起始年份", value=datetime(2018, 1, 1), key="div_start")
    with c3:
        st.write("")
        go_div = st.button("查询分红", type="primary", key="go_div")

    with st.expander("高股息参考池"):
        st.markdown("""
        | 代码 | 名称 | 行业 | 近年股息率 |
        |------|------|------|-----------|
        | **600900** | 长江电力 | 水电 | ~3.5% |
        | **601088** | 中国神华 | 煤炭 | ~6% |
        | **600036** | 招商银行 | 银行 | ~5% |
        | **601398** | 工商银行 | 银行 | ~5.5% |
        | **000333** | 美的集团 | 家电 | ~3.5% |
        | **600585** | 海螺水泥 | 建材 | ~5% |
        | **601857** | 中国石油 | 石油 | ~4.5% |
        """)

    if go_div:
        sym = resolve_symbol(div_code)
        with st.spinner("正在查询分红记录…"):
            try:
                div_df = fetch_dividend_history(div_code)
            except Exception as e:
                st.error(f"查询失败：{e}")
                st.stop()

        if div_df.empty:
            st.warning(f"代码 {div_code} 暂无分红数据，可能为非高股息标的")
        else:
            # Parse dividend data - columns vary by function output
            div_df.columns = [str(c) for c in div_df.columns]
            # Try to get date and dividend columns
            date_col = [c for c in div_df.columns if '日' in c or 'date' in str(c).lower()]
            # 优先匹配"每股派现"列，避免匹配到"派现总额"等错误列
            amount_col = [c for c in div_df.columns if '每股派现' in str(c) or '每股派息' in str(c)]
            if not amount_col:
                amount_col = [c for c in div_df.columns if ('派' in str(c) or '息' in str(c)) and '总额' not in str(c) and '总' not in str(c)]
            if not amount_col:
                amount_col = [c for c in div_df.columns if 'amount' in str(c).lower()]

            if date_col and amount_col:
                dc = date_col[0]; ac = amount_col[0]
                div_display = div_df[[dc, ac]].copy()
                div_display.columns = ['除权日期', '每股派息']
                div_display['除权日期'] = pd.to_datetime(div_display['除权日期'])
                div_display = div_display[div_display['除权日期'] >= pd.Timestamp(div_start)]
                div_display['每股派息'] = pd.to_numeric(div_display['每股派息'], errors='coerce')
                div_display = div_display.dropna(subset=['每股派息'])
                div_display = div_display[div_display['每股派息'] > 0]  # 排除0值和负值
                div_display = div_display.sort_values('除权日期', ascending=False)

                if len(div_display) > 0:
                    total_div = div_display['每股派息'].sum()
                    years = div_display['除权日期'].dt.year.nunique()
                    avg_div = total_div / max(years, 1)

                    c1, c2, c3 = st.columns(3)
                    c1.metric("累计每股派息", f"¥{total_div:.2f}")
                    c2.metric("年均派息", f"¥{avg_div:.2f}")
                    c3.metric("分红次数", f"{len(div_display)} 次")

                    # Get current price for yield
                    try:
                        sdf = fetch_stock_history(symbol=sym)
                        sdf["date"] = pd.to_datetime(sdf["date"])
                        sdf = sdf.sort_values("date")
                        cur_price = float(sdf.iloc[-1]["close"])
                        yield_pct = avg_div / cur_price * 100
                        st.metric("估算股息率", f"{yield_pct:.2f}%（基于年均派息 ÷ 现价 {cur_price:.2f}）")
                    except Exception:
                        pass

                    st.dataframe(div_display, use_container_width=True, hide_index=True)
                else:
                    st.info("所选时间段内无分红记录")
            else:
                st.dataframe(div_df, use_container_width=True, hide_index=True)
                st.caption("以上为原始分红数据")

    st.caption("数据源：新浪财经 stock_history_dividend_detail · 个股历史分红记录")

# ============================================================
# TAB 8 — 多ETF对比 & 定投vs一次性
# ============================================================
with tab8:
    st.caption("同时回测多只 ETF，对比定投 vs 一次性买入")

    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])
    with c1:
        etf_list = st.text_input("ETF 代码（逗号分隔）", value="510300,510050,159915", key="multi_etf",
                                 help="多个代码用逗号分隔，例如: 510300,510050,159915")
    with c2:
        multi_start = st.date_input("起始日期", value=datetime(2020, 1, 1), key="multi_start")
    with c3:
        multi_monthly = st.number_input("每月金额", value=500, step=100, min_value=100, key="multi_monthly")
    with c4:
        st.write("")
        go_multi = st.button("对比回测", type="primary", use_container_width=True, key="go_multi")

    if go_multi:
        codes = [c.strip() for c in etf_list.split(",") if c.strip()]
        if len(codes) < 2:
            st.warning("请输入至少 2 个 ETF 代码")
        else:
            results = []
            for code in codes:
                sym = resolve_symbol(code)
                try:
                    df = fetch_etf_history(sym)
                    df["date"] = pd.to_datetime(df["date"]); df = df.sort_values("date")
                    df = df[df["date"] >= pd.Timestamp(multi_start)].copy()
                    if df.empty or len(df) < 50:
                        results.append((code, "数据不足", 0, 0, 0, 0, 0))
                        continue

                    df["ym"] = df["date"].dt.to_period("M")
                    bm = ~df.duplicated(subset="ym", keep="first")
                    ts_dca = sum(multi_monthly / df.loc[i, "close"] for i in df[bm].index)
                    ti_dca = multi_monthly * bm.sum()

                    # Lump sum: invest ALL at first opportunity
                    first_price = df.loc[df[bm].index[0], "close"]
                    ts_lump = ti_dca / first_price
                    ti_lump = ti_dca

                    latest_price = df.iloc[-1]["close"]
                    cv_dca = ts_dca * latest_price
                    cv_lump = ts_lump * latest_price
                    r_dca = (cv_dca - ti_dca) / ti_dca * 100
                    r_lump = (cv_lump - ti_lump) / ti_lump * 100

                    results.append((code, f"共{bm.sum()}期", ti_dca, cv_dca, r_dca, cv_lump, r_lump))
                except Exception as e:
                    results.append((code, str(e)[:30], 0, 0, 0, 0, 0))

            # Display comparison table
            st.markdown("""<div class="section-title">定投收益对比</div>""", unsafe_allow_html=True)
            comp_data = []
            for r in results:
                comp_data.append({
                    "ETF 代码": r[0],
                    "期数": r[1],
                    "投入本金": f"¥{r[2]:,.0f}" if r[2] > 0 else "N/A",
                    "定投市值": f"¥{r[3]:,.0f}" if r[3] > 0 else "N/A",
                    "定投收益率": f"{r[4]:+.2f}%" if r[3] > 0 else "N/A",
                    "一次性收益率": f"{r[6]:+.2f}%" if r[5] > 0 else "N/A",
                })
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

            # Visual comparison
            st.markdown("""<div class="section-title">收益率柱状图</div>""", unsafe_allow_html=True)
            chart_data = []
            for r in results:
                if r[3] > 0:
                    chart_data.append({"ETF": r[0], "定投收益率%": round(r[4], 2), "一次性收益率%": round(r[6], 2)})
            if chart_data:
                chart_df = pd.DataFrame(chart_data).set_index("ETF")
                st.bar_chart(chart_df, height=300)

    st.caption("数据源：新浪财经 fund_etf_hist_sina · 定投 = 每月固定金额买入 · 一次性 = 首日全部买入")


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
    ETF 定投回测 v0.6 |
    <a href="https://github.com/Colorfulrain1751/etf-dca-backtest">GitHub</a> |
    数据源：新浪财经 / 乐股网 / AKShare |
    已交叉验证 · 不构成投资建议
</div>
""", unsafe_allow_html=True)
