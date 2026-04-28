# Trade News Project Setup Guide

## Project Structure

```
trade-news-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB connection
│   ├── routers/
│   │   ├── news.py          # News endpoints
│   │   ├── markets.py       # Market data endpoints
│   │   └── signals.py       # Trading signals
│   ├── services/
│   │   ├── news_fetcher.py  # News API integrations
│   │   ├── market_data.py   # Market data APIs
│   │   └── signal_gen.py    # Signal generation logic
│   └── utils/
│       ├── cache.py         # Caching logic
│       └── helpers.py       # Helper functions
├── requirements.txt
├── .env
└── README.md

trade-news-frontend/
├── index.html               # The file Sami sent (modified)
├── js/
│   └── api.js              # API integration layer
└── README.md
```

## Initial Setup

### 1. Create Virtual Environment
```bash
cd /home/claude
mkdir trade-news-backend
cd trade-news-backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv requests aiohttp pydantic redis httpx feedparser yfinance python-multipart
```

### 3. Environment Variables (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# APIs
NEWSAPI_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_key_here
TWELVE_DATA_KEY=your_key_here

# Server
PORT=8000
ENVIRONMENT=development
```

## API Keys to Get (All Free Tier)

1. **NewsAPI.org**: https://newsapi.org/register
   - Free: 100 requests/day
   
2. **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
   - Free: 25 requests/day
   
3. **Twelve Data**: https://twelvedata.com/pricing
   - Free: 800 requests/day
   
4. **ExchangeRate-API**: https://www.exchangerate-api.com/
   - Free: 1500 requests/month

5. **Supabase** (Database): https://supabase.com/
   - Free tier: Unlimited projects

## Next Steps

After setup:
1. Test database connection
2. Create initial models
3. Build news fetcher
4. Build market data fetcher
5. Integrate with frontend
