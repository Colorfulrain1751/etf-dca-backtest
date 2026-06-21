"""
ETF 定投回测工具 — 最简版 v0.1
客户：星辰财富管理公司
"""

import streamlit as st
import akshare as ak
import pandas as pd
from datetime import datetime

# ---------- 页面设置 ----------
st.set_page_config(page_title="ETF定投回测", page_icon="📈")
st.title("📈 ETF 定投回测")
st.caption("输入三个数，看你的定投是赚是亏")

# ---------- 用户输入 ----------
col1, col2, col3 = st.columns(3)
with col1:
    code_input = st.text_input(
        "ETF 代码",
        value="510300",
        help="沪市 ETF 以 51/56/58 开头，深市 ETF 以 159/16 开头",
    )
with col2:
    start_date = st.date_input("开始定投日期", value=datetime(2020, 1, 1))
with col3:
    monthly = st.number_input("每月定投金额（元）", value=500, step=100, min_value=100)

# 常用 ETF 快捷参考
with st.expander("📋 常用 ETF 代码参考"):
    st.markdown("""
    | 代码 | 名称 | 代码 | 名称 |
    |------|------|------|------|
    | 510300 | 沪深300ETF | 510500 | 中证500ETF |
    | 510050 | 上证50ETF | 159915 | 创业板ETF |
    | 588000 | 科创50ETF | 512880 | 证券ETF |
    | 512100 | 中证1000ETF | 513100 | 纳指ETF |
    | 159941 | 纳指ETF(深) | 510880 | 红利ETF |
    """)

# ---------- 计算按钮 ----------
if st.button("开始回测", type="primary"):

    with st.spinner("正在从新浪财经获取真实行情数据..."):

        # 构造新浪 symbol 格式
        # 深市: 0xxxxx/3xxxxx 股票, 159xxx/16xxxx ETF
        # 沪市: 其余均为沪市
        if code_input.startswith("159") or code_input.startswith("16"):
            symbol = f"sz{code_input}"
        elif code_input.startswith("0") or code_input.startswith("3"):
            symbol = f"sz{code_input}"
        else:
            symbol = f"sh{code_input}"

        try:
            df = ak.fund_etf_hist_sina(symbol=symbol)
        except Exception as e:
            st.error(f"获取数据失败，可能原因：\n1. 代码 {code_input} 不存在\n2. 网络请求超时\n\n原始错误：{e}")
            st.stop()

    if df.empty:
        st.error(f"代码 {code_input} 没有返回数据，请检查代码是否正确。\n\n提示：沪市 ETF 以 51/56/58 开头，深市 ETF 以 159/16 开头。")
        st.stop()

    # ---------- 数据清洗 ----------
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # 按用户选择的开始日期过滤
    df = df[df["date"] >= pd.Timestamp(start_date)].copy()
    if df.empty:
        st.error("所选日期范围内没有数据，请换个起始日期")
        st.stop()

    # ---------- 模拟定投 ----------
    # 每个自然月，取第一个交易日，以收盘价买入
    df["ym"] = df["date"].dt.to_period("M")
    buy_mask = ~df.duplicated(subset="ym", keep="first")

    total_shares = 0.0
    total_invested = 0

    for i in df[buy_mask].index:
        price = df.at[i, "close"]
        total_shares += monthly / price
        total_invested += monthly

    # 标记买入点
    df["buy_price"] = None
    df.loc[buy_mask, "buy_price"] = df.loc[buy_mask, "close"]

    # ---------- 计算结果 ----------
    latest_price = df.iloc[-1]["close"]
    latest_date = df.iloc[-1]["date"]
    current_value = total_shares * latest_price
    profit = current_value - total_invested
    return_pct = (profit / total_invested) * 100
    periods = int(total_invested // monthly)

    # ---------- 显示结果 ----------
    st.divider()
    st.subheader("📊 回测结果")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("累计投入本金", f"¥{total_invested:,.0f}")
    col2.metric("当前市值", f"¥{current_value:,.0f}", delta=f"¥{profit:,.0f}")
    col3.metric("总收益率", f"{return_pct:+.2f}%")
    col4.metric("定投期数", f"{periods} 期")

    st.caption(f"数据截止：{latest_date.strftime('%Y-%m-%d')} | 最新价格：{latest_price:.4f} 元")

    # ---------- 走势图 ----------
    st.subheader("📈 价格走势与买入点")
    chart_df = df.set_index("date")
    st.line_chart(chart_df[["close", "buy_price"]], height=400)
    st.caption("蓝线：ETF 价格 | 红线/标记：你每次定投买入的位置")
