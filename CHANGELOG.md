# Changelog

All notable changes to ETF DCA Backtest will be documented here.

---

## v0.2 — 2026-06-21

### Added
- **Market Environment tab** — real-time analysis panel
  - 5 major index snapshots (SSE, CSI300, CSI500, ChiNext, STAR50)
  - CSI300 PE valuation thermometer with historical percentile gauge
  - Market-wide PB valuation analysis
  - SSE Composite MA20/MA60 trend chart
  - Composite market signal summary
- **Yearly breakdown table** — annual DCA buy summary
- **Changelog tab** — in-app version history
- **`@st.cache_data`** — data caching for faster reloads

### Changed
- **UI redesign** — tab-based layout, card-style metrics, color-coded P&L
- **Custom CSS** — professional styling with red/green Chinese market convention
- **Wide layout** — uses full screen width

### Fixed
- Deep market ETF code prefix (159xxx → sz, was incorrectly sh)

---

## v0.1 — 2026-06-21

### Added
- Initial release
- ETF DCA backtest with real data (Sina Finance via AKShare)
- Buy-point visualization on price chart
- Deployed to Streamlit Cloud

---

**Roadmap:** multi-ETF comparison → weekly DCA → fee simulation → strategy comparison → user accounts
