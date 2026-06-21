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
# TAB 5 — 资金流向
# ============================================================
with tab5:
    st.caption("数据源：东方财富 / 新浪财经 · 沪深港通 + 行业资金流向")

    # --- Northbound ---
    st.markdown("""<div class="section-title">沪深港通 · 北上资金</div>""", unsafe_allow_html=True)

    try:
        nb_flow = fetch_northbound_summary()
        if len(nb_flow) > 0:
            # Parse the summary table
            nb_cols = st.columns(4)
            labels = ["沪股通", "深股通", "北上合计", "南下合计"]
            for i, (col, label) in enumerate(zip(nb_cols, labels)):
                if i < len(nb_flow):
                    row = nb_flow.iloc[i]
                    with col:
                        net = float(row.iloc[3]) if len(row) > 3 else 0
                        st.metric(label, f"{net/1e8:.1f} 亿",
                                  delta=f"{net/1e8:+.1f} 亿" if net != 0 else None)
    except Exception as e:
        st.warning(f"北上资金数据暂不可用: {e}")

    # Northbound trend chart
    try:
        nb_hist = fetch_northbound_hist()
        nb_hist.columns = ['日期', '当日成交净买额', '买入成交额', '卖出成交额', '沪深300', '上证指数', '深证成指']
        nb_hist['日期'] = pd.to_datetime(nb_hist['日期'])
        nb_hist = nb_hist.sort_values('日期').tail(120)
        nb_hist['累计净买额'] = nb_hist['当日成交净买额'].astype(float).cumsum()

        st.line_chart(nb_hist.set_index('日期')[['当日成交净买额']], height=250, color=["#1a56db"])
        st.caption("数据源：东方财富 stock_hsgt_hist_em (2692 条历史数据) · 近 120 个交易日")
    except Exception as e:
        st.warning(f"北上资金历史数据暂不可用: {e}")

    # --- Sector Flow ---
    st.markdown("""<div class="section-title">行业板块资金流向</div>""", unsafe_allow_html=True)

    try:
        sector = fetch_sector_spot()
        if len(sector) > 0:
            # Limit to top 15 by change magnitude
            sector_display = sector.head(15).copy()
            display_cols = ['label', '涨跌幅']
            # Try to find the right columns
            for c in sector.columns:
                if '涨跌' in str(c) and '幅' in str(c):
                    display_cols[1] = c
                    break

            cols = st.columns(5)
            for i, (_, row) in enumerate(sector_display.iterrows()):
                ci = i % 5
                name = str(row.iloc[0])
                try:
                    chg = float(row.iloc[3]) if len(row) > 3 else float(row.iloc[1])
                except Exception:
                    chg = 0
                color = "#059669" if chg >= 0 else "#dc2626"
                with cols[ci]:
                    st.markdown(f"""
                    <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;
                                border:1px solid #e5e7eb;margin-bottom:6px;">
                        <div style="font-size:0.8rem;color:#6b7280;">{name}</div>
                        <div style="font-weight:700;color:{color};">{chg:+.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"行业板块数据暂不可用: {e}")

    st.caption("数据源：新浪财经 stock_sector_spot (49 个行业)")

# ============================================================
# TAB 6 — 恐贪指数
# ============================================================
with tab6:
    st.caption("基于 PE 分位、成交量、RSI、北上资金合成的市场情绪指标")

    score_parts = {}
    fgi_signals = []

    # 1. PE score (20 = max fear / cheap, 80 = max greed / expensive)
    try:
        pe_df = fetch_index_pe("沪深300")
        pe_df["日期"] = pd.to_datetime(pe_df["日期"]); pe_df = pe_df.sort_values("日期")
        recent_pe = pe_df.tail(250)
        pe_pct = float(recent_pe.iloc[-1]["动态市盈率分位"])
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

    # 4. Northbound score
    try:
        nb = fetch_northbound_hist()
        nb.columns = ['日期','当日成交净买额','买入成交额','卖出成交额','沪深300','上证指数','深证成指']
        nb['date'] = pd.to_datetime(nb['日期']); nb = nb.sort_values('date')
        recent_nb = nb.tail(20)
        nb_net = float(recent_nb['当日成交净买额'].sum())
        nb_score = 50 + (nb_net / 1e10) * 5
        nb_score = min(100, max(0, nb_score))
        score_parts["北上资金"] = nb_score
        if nb_net > 50: fgi_signals.append(("北上资金", "green", f"近20日净流入 {nb_net/1e8:.1f} 亿"))
        elif nb_net < -50: fgi_signals.append(("北上资金", "red", f"近20日净流出 {abs(nb_net)/1e8:.1f} 亿"))
        else: fgi_signals.append(("北上资金", "yellow", f"近20日 {nb_net/1e8:+.1f} 亿"))
    except Exception as e:
        nb_score = 50

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

    st.caption("数据源：乐股网(PE分位) · 新浪财经(成交量/RSI) · 东方财富(北上资金) · 复合计算")

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
            amount_col = [c for c in div_df.columns if '派' in str(c) or '息' in str(c) or '金' in str(c) or 'amount' in str(c).lower()]

            if date_col and amount_col:
                dc = date_col[0]; ac = amount_col[0]
                div_display = div_df[[dc, ac]].copy()
                div_display.columns = ['除权日期', '每股派息']
                div_display['除权日期'] = pd.to_datetime(div_display['除权日期'])
                div_display = div_display[div_display['除权日期'] >= pd.Timestamp(div_start)]
                div_display['每股派息'] = div_display['每股派息'].astype(float)
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
