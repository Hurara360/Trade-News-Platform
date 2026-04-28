"""
FastAPI Backend — Trade News Platform
Sentiment-driven signal API + market data endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))

from news_fetcher import NewsFetcher
from market_data import MarketDataFetcher
from signal_generator import SignalGenerator

app = FastAPI(title="Trade News Intelligence API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service singletons
news_fetcher    = NewsFetcher()
market_fetcher  = MarketDataFetcher()
signal_generator = SignalGenerator()

# Simple in-memory cache
_cache: dict = {}
_cache_ts: dict = {}
NEWS_TTL    = 300   # 5 min
SIGNAL_TTL  = 300   # 5 min
MARKET_TTL  = 60    # 1 min


def _fresh(key: str, ttl: int) -> bool:
    ts = _cache_ts.get(key)
    return bool(ts and (datetime.now() - ts).seconds < ttl)


# ─────────────────────────────────────────────────────────────────────────────
# Root
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name":    "Trade News Intelligence API",
        "version": "2.0.0",
        "endpoints": {
            "sentiment_signals": "/api/sentiment-signals",
            "news":              "/api/news/{category}",
            "markets":           "/api/markets/{category}",
            "all_data":          "/api/all",
            "health":            "/api/health",
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Sentiment Signals  ← main new endpoint
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/sentiment-signals")
def get_sentiment_signals():
    """
    Fetch news across all categories, run entity detection + sentiment analysis,
    and return ranked trading signals with full reasoning chain.
    """
    key = "sentiment_signals"
    if _fresh(key, SIGNAL_TTL) and key in _cache:
        return JSONResponse(content=_cache[key])

    try:
        articles = news_fetcher.fetch_all_categories()
        signals  = signal_generator.generate_from_articles(articles)
        summary  = signal_generator.get_summary(signals)

        # Top market movers (entities ranked by mention count)
        from entity_tracker import EntityTracker
        top_movers = EntityTracker().top_movers(articles, top_n=8)

        payload = {
            "signals":     signals,
            "summary":     summary,
            "top_movers":  top_movers,
            "article_count": len(articles),
            "timestamp":   datetime.now().isoformat(),
        }

        _cache[key]    = payload
        _cache_ts[key] = datetime.now()

        return JSONResponse(content=payload)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# News
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/news/{category}")
def get_news(category: str):
    valid = ['war', 'trade', 'markets', 'central_banks', 'crypto', 'energy', 'tech']
    if category not in valid:
        raise HTTPException(status_code=400, detail=f"Category must be one of {valid}")

    key = f"news_{category}"
    if _fresh(key, NEWS_TTL) and key in _cache:
        return JSONResponse(content={"data": _cache[key]})

    try:
        articles = news_fetcher.aggregate_all(category)
        _cache[key]    = articles
        _cache_ts[key] = datetime.now()
        return JSONResponse(content={"data": articles})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Markets
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/markets/{category}")
def get_markets(category: str):
    valid = ['forex', 'crypto', 'stocks', 'commodities']
    if category not in valid:
        raise HTTPException(status_code=400, detail=f"Category must be one of {valid}")

    key = f"markets_{category}"
    if _fresh(key, MARKET_TTL) and key in _cache:
        return JSONResponse(content={"data": _cache[key]})

    try:
        all_markets = market_fetcher.fetch_all_markets()
        data = all_markets.get(category, [])
        _cache[key]    = data
        _cache_ts[key] = datetime.now()
        return JSONResponse(content={"data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Legacy signals endpoint (kept for compatibility)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/signals")
def get_signals():
    key = "sentiment_signals"
    if _fresh(key, SIGNAL_TTL) and key in _cache:
        payload = _cache[key]
        return JSONResponse(content={"data": payload.get("signals", [])})

    # Trigger fresh fetch via main endpoint logic
    resp = get_sentiment_signals()
    return JSONResponse(content={"data": _cache.get("sentiment_signals", {}).get("signals", [])})


# ─────────────────────────────────────────────────────────────────────────────
# All data (initial page load)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/all")
def get_all_data():
    try:
        # News
        news = {
            cat: news_fetcher.aggregate_all(cat)[:6]
            for cat in ['war', 'trade', 'markets']
        }

        # Signals
        articles = news_fetcher.fetch_all_categories()
        signals  = signal_generator.generate_from_articles(articles)
        summary  = signal_generator.get_summary(signals)

        # Markets
        markets = market_fetcher.fetch_all_markets()

        return JSONResponse(content={
            "data": {
                "news":      news,
                "markets":   markets,
                "signals":   signals[:20],
                "summary":   summary,
                "timestamp": datetime.now().isoformat(),
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status":    "healthy",
        "version":   "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "newsapi":   bool(news_fetcher.newsapi_key),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
