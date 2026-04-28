"""
FastAPI Backend for Trade News Platform
Main application file
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import our services
from news_fetcher import NewsFetcher
from market_data import MarketDataFetcher
from signal_generator import SignalGenerator

app = FastAPI(title="Trade News API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
news_fetcher = NewsFetcher()
market_fetcher = MarketDataFetcher()
signal_generator = SignalGenerator()

# In-memory cache (use Redis in production)
cache = {
    'news': {},
    'markets': {},
    'signals': {},
    'last_updated': {}
}

CACHE_DURATION = 300  # 5 minutes


@app.get("/")
def read_root():
    return {
        "message": "Trade News API",
        "version": "1.0.0",
        "endpoints": {
            "news": "/api/news/{category}",
            "markets": "/api/markets/{category}",
            "signals": "/api/signals",
            "all_data": "/api/all"
        }
    }


@app.get("/api/news/{category}")
def get_news(category: str):
    """
    Get news for specific category: war, trade, markets
    """
    if category not in ['war', 'trade', 'markets']:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Check cache
    cache_key = f"news_{category}"
    if cache_key in cache['news']:
        cached_time = cache['last_updated'].get(cache_key)
        if cached_time and (datetime.now() - cached_time).seconds < CACHE_DURATION:
            return JSONResponse(content={'data': cache['news'][cache_key]})
    
    # Fetch fresh data
    try:
        articles = news_fetcher.aggregate_all(category)
        
        # Update cache
        cache['news'][cache_key] = articles
        cache['last_updated'][cache_key] = datetime.now()
        
        return JSONResponse(content={'data': articles})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/markets/{category}")
def get_markets(category: str):
    """
    Get market data for specific category: forex, crypto, stocks, commodities
    """
    if category not in ['forex', 'crypto', 'stocks', 'commodities']:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Check cache
    cache_key = f"markets_{category}"
    if cache_key in cache['markets']:
        cached_time = cache['last_updated'].get(cache_key)
        if cached_time and (datetime.now() - cached_time).seconds < 60:  # 1 min cache
            return JSONResponse(content={'data': cache['markets'][cache_key]})
    
    # Fetch fresh data
    try:
        all_markets = market_fetcher.fetch_all_markets()
        category_data = all_markets.get(category, [])
        
        # Update cache
        cache['markets'][cache_key] = category_data
        cache['last_updated'][cache_key] = datetime.now()
        
        return JSONResponse(content={'data': category_data})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals")
def get_signals():
    """
    Get all trading signals
    """
    # Check cache
    cache_key = "signals_all"
    if cache_key in cache['signals']:
        cached_time = cache['last_updated'].get(cache_key)
        if cached_time and (datetime.now() - cached_time).seconds < CACHE_DURATION:
            return JSONResponse(content={'data': cache['signals'][cache_key]})
    
    # Generate fresh signals
    try:
        signals = signal_generator.generate_all_signals()
        
        # Update cache
        cache['signals'][cache_key] = signals
        cache['last_updated'][cache_key] = datetime.now()
        
        return JSONResponse(content={'data': signals})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/all")
def get_all_data():
    """
    Get all data: news, markets, signals (for initial page load)
    """
    try:
        data = {
            'news': {
                'war': news_fetcher.aggregate_all('war')[:5],
                'trade': news_fetcher.aggregate_all('trade')[:5],
                'markets': news_fetcher.aggregate_all('markets')[:5]
            },
            'markets': market_fetcher.fetch_all_markets(),
            'signals': signal_generator.generate_all_signals(),
            'timestamp': datetime.now().isoformat()
        }
        
        return JSONResponse(content={'data': data})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
