"""
ETF 定投回测 · 市场分析 — 主页
"""

import streamlit as st

st.set_page_config(
    page_title="ETF DCA · 智能投资分析",
    page_icon="▸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    @keyframes gradientFlow {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    .hero {
        text-align: center; padding: 60px 20px 50px 20px;
        animation: fadeUp 0.8s ease-out;
    }
    .hero h1 {
        font-size: 3rem; font-weight: 800; color: #111;
        letter-spacing: -0.5px; margin-bottom: 12px;
    }
    .hero .gradient {
        background: linear-gradient(135deg, #1a56db, #7c3aed, #db2777);
        background-size: 200% 200%;
        animation: gradientFlow 6s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero .tagline {
        font-size: 1.15rem; color: #6b7280;
        max-width: 600px; margin: 16px auto 28px auto;
        line-height: 1.7;
    }
    .hero .cta {
        display: inline-block; background: #1a56db; color: #fff;
        padding: 12px 32px; border-radius: 10px; font-size: 1rem;
        font-weight: 700; text-decoration: none;
        transition: all 0.2s ease;
        box-shadow: 0 4px 16px rgba(26,86,219,0.25);
    }
    .hero .cta:hover {
        background: #1e40af; transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(26,86,219,0.35);
    }

    .feature-card {
        background: #fff; border: 1px solid #e5e7eb;
        border-radius: 16px; padding: 28px 24px;
        transition: all 0.25s ease;
        animation: fadeUp 0.8s ease-out backwards;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.08);
        border-color: #1a56db;
    }
    .feature-card:nth-child(1) { animation-delay: 0.1s; }
    .feature-card:nth-child(2) { animation-delay: 0.2s; }
    .feature-card:nth-child(3) { animation-delay: 0.3s; }
    .feature-icon {
        font-size: 2rem; margin-bottom: 12px;
    }
    .feature-card h3 {
        font-size: 1.1rem; font-weight: 700; color: #111;
        margin-bottom: 8px;
    }
    .feature-card p {
        font-size: 0.9rem; color: #6b7280; line-height: 1.6;
    }

    .steps {
        display: flex; gap: 24px; justify-content: center;
        margin-top: 12px;
    }
    .step {
        text-align: center; flex: 1; max-width: 240px;
        animation: fadeUp 0.8s ease-out backwards;
    }
    .step:nth-child(1) { animation-delay: 0.15s; }
    .step:nth-child(2) { animation-delay: 0.30s; }
    .step:nth-child(3) { animation-delay: 0.45s; }
    .step-num {
        width: 48px; height: 48px; border-radius: 50%;
        background: linear-gradient(135deg, #1a56db, #7c3aed);
        color: #fff; font-size: 1.3rem; font-weight: 800;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 12px auto;
    }
    .step h4 { font-size: 1rem; font-weight: 700; color: #111; margin-bottom: 4px; }
    .step p  { font-size: 0.85rem; color: #6b7280; }

    .divider {
        width: 60px; height: 3px; background: linear-gradient(90deg, #1a56db, #7c3aed);
        border-radius: 2px; margin: 0 auto 24px auto;
    }

    .footer-home {
        text-align: center; color: #9ca3af; font-size: 0.82rem;
        margin-top: 64px; padding: 24px 0; border-top: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <h1>
        用数据看懂市场<br>
        <span class="gradient">不再凭感觉投资</span>
    </h1>
    <p class="tagline">
        基于真实行情数据，3 秒完成定投回测、估值分析和个股技术诊断。
        让每一次决策都有数据支撑，而不是"听别人说"。
    </p>
</div>
""", unsafe_allow_html=True)

_, cta_btn, _ = st.columns([1, 1, 1])
with cta_btn:
    if st.button("开始使用", type="primary", use_container_width=True):
        st.switch_page("pages/1_Analysis.py")

# ============================================================
# FEATURES
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">▸</div>
        <h3>定投回测</h3>
        <p>
            输入 ETF 代码、起始日期和金额，立刻算出累计投入、当前市值和收益率。
            真实前复权数据，覆盖 2011 年至今所有 A 股 ETF。
        </p>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">◉</div>
        <h3>估值温度计</h3>
        <p>
            实时追踪沪深300 PE/PB 历史分位，用颜色告诉你市场是贵还是便宜。
            别人贪婪时恐惧，别人恐惧时贪婪。
        </p>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">◎</div>
        <h3>个股技术分析</h3>
        <p>
            MA 均线、MACD、RSI、布林带 — 六大指标自动计算，
            金叉死叉自动标注，支撑阻力一眼看懂。
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HOW IT WORKS
# ============================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center;font-weight:800;color:#111;'>三步开始</h2>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("""
    <div class="step">
        <div class="step-num">1</div>
        <h4>输入代码</h4>
        <p>ETF 或股票代码，510300、600036 都可以</p>
    </div>
    """, unsafe_allow_html=True)
with s2:
    st.markdown("""
    <div class="step">
        <div class="step-num">2</div>
        <h4>设定参数</h4>
        <p>选起始日期和金额，点一下开始分析</p>
    </div>
    """, unsafe_allow_html=True)
with s3:
    st.markdown("""
    <div class="step">
        <div class="step-num">3</div>
        <h4>看结论</h4>
        <p>绿色低估、红色高估、关键价位 — 秒懂</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div class="footer-home">
    数据来源：新浪财经 / 乐股网 / AKShare &nbsp;|&nbsp;
    不构成投资建议 &nbsp;|&nbsp;
    <a href="https://github.com/Colorfulrain1751/etf-dca-backtest">GitHub</a>
</div>
""", unsafe_allow_html=True)
