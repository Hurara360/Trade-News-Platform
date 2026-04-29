# SIGNAL WIRE — News-Driven Trade Intelligence v2.0

Bloomberg Terminal-style financial dashboard. Generates **real trading signals** from live news by detecting market-moving entities and scoring their sentiment.

---

## What Changed in v2.0

### 1. Professional Color Scheme
Deep navy layered backgrounds (`#070A0F` → `#232E48`) with warm amber gold (`#D4A843`), teal-green BUY (`#10B981`), coral-red SELL (`#EF4444`). Inter + IBM Plex Mono typography. No more pure-black backgrounds — proper depth and hierarchy.

### 2. Clickable News Sources
Every news card has a **"Read Full Article"** link that opens the original source in a new tab. Cards expand on click to show the summary + link. Signal chain modal also links to the source article.

### 3. No Fake Data
`Math.random()` has been completely removed from all displayed values. Instead:
- **Skeleton loading** states (animated shimmer) while data fetches
- **"Data temporarily unavailable"** messages with a Retry button on failure
- **"N/A"** shown for any value that cannot be obtained from the API
- Charts show only real CoinGecko price history — never simulated

### 4. Engagement Features
| Feature | How it works |
|---|---|
| Sentiment Gauge | SVG half-circle needle, updates from signal summary's buy/sell ratio |
| Market Heatmap | Color-coded grid (green intensity = % gain, red = % loss) from real market data |
| Expandable News Cards | Click any card to expand; chevron rotates; click again to collapse |
| News Search + Filter | Live text search + BREAKING urgency filter on both news feeds |
| Chart Timeframe Selector | 1D / 1W / 1M buttons fetch real CoinGecko historical data |
| Signal Chain Modal | Click any signal to see full reasoning chain (News → Entity → Sentiment → Asset → Signal) |
| Signal Filters | ALL / BUY / SELL / HIGH CONF filter chips on the signal feed |
| Asset Switcher | BTC / ETH / SOL buttons on the chart |

### 5. Optimised API Usage
See `js/api.js` — all caching and rate limiting lives there.

---

## Architecture

```
trade-news-platform/
├── index.html              # Frontend — single-page app
├── js/
│   └── api.js              # Smart API client (v2.0)
└── backend/
    ├── main.py             # FastAPI app
    ├── news_fetcher.py     # RSS + NewsAPI + GDELT aggregator
    ├── signal_generator.py # Orchestrates signal pipeline
    ├── sentiment_engine.py # Keyword-weighted sentiment scorer
    ├── entity_tracker.py   # 30+ market-moving entity detector
    ├── asset_mapper.py     # Entity + sentiment → trade signal
    └── market_data.py      # yfinance market prices
```

---

## How Caching Works (`js/api.js`)

```javascript
// Every fetch is cache-first:
_fetch(url, cacheKey, ttl)
// → checks localStorage for sw2_{cacheKey}
// → if fresh: returns cached data immediately (no network)
// → if expired: fetches live, stores result with new TTL
```

| Data type | Cache TTL | Auto-refresh interval |
|---|---|---|
| Signals | 5 min | 5 min |
| Markets | 5 min | 5 min |
| News | 30 min | 30 min |
| Charts | 10 min | on-demand |

**Pausing**: Auto-refresh stops when the tab is hidden (Page Visibility API) or the user is idle for 5+ minutes. Resumes immediately when the tab comes back into focus or the user moves the mouse.

**Daily limits**: NewsAPI (100/day) and Alpha Vantage (25/day) are tracked in localStorage. When usage reaches 92% of the limit, the system stops calling that API and falls back to RSS/GDELT/CoinGecko (all unlimited).

---

## How Signals Are Generated

```
News Article
    ↓
Entity Detection  (Fed, ECB, Trump, OPEC, SEC, NVDA, BTC…)
    ↓
Sentiment Scoring (keyword-weighted bullish/bearish score)
    ↓
Asset Mapping     (entity + sentiment → affected asset + direction)
    ↓
Signal            { asset, BUY/SELL/HOLD, confidence%, reason, source }
```

No external AI API is used — all processing is keyword-based Python running on the Railway backend.

---

## Customisation

Edit `js/api.js` → `SW_CONFIG`:

```javascript
SW_CONFIG.TTL.signals     = 5 * 60 * 1000;  // Change signal cache TTL
SW_CONFIG.INTERVALS.news  = 30 * 60 * 1000; // Change news refresh rate
SW_CONFIG.IDLE_TIMEOUT    = 5 * 60 * 1000;  // Change idle pause threshold
SW_CONFIG.DAILY_LIMITS.newsapi = 100;        // Adjust if on paid plan
```

---

## Backend Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/sentiment-signals` | Main — signals + summary + top movers |
| `GET /api/news/{category}` | News for: war, trade, markets, central_banks, crypto, energy, tech |
| `GET /api/markets/{category}` | Prices for: forex, crypto, stocks, commodities |
| `GET /api/all` | Initial page load bundle |
| `GET /api/health` | Health check |

Backend is deployed on Railway: `https://bountiful-consideration-production.up.railway.app`

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # add NEWSAPI_KEY
uvicorn main:app --reload

# Frontend — just open index.html in a browser
# (or use Live Server in VS Code)
```
