# 📈 ETF DCA Backtest

A real-time ETF dollar-cost averaging (DCA) backtesting tool for Chinese A-share ETFs.

**Live demo:** *(coming soon)*

## Features

- **Real data** — historical prices from Sina Finance via AKShare (2011–present)
- **DCA simulation** — monthly fixed-amount buying on the first trading day
- **Multi-ETF** — supports all Shanghai (51xxxx) and Shenzhen (159xxx) ETFs
- **Instant results** — total invested, current value, return %, buy-point chart

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. Enter ETF code (e.g., `510300` for CSI 300 ETF)
2. Select DCA start date
3. Set monthly investment amount
4. Click "开始回测"

## Tech Stack

- [Streamlit](https://streamlit.io) — web UI
- [AKShare](https://github.com/akfamily/akshare) — financial data
- [Pandas](https://pandas.pydata.org) — data processing

## License

MIT
