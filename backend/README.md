# Trade News Platform - Quick Start

## 🎯 What You're Building

A real-time trading news & signals platform with:
- Live news from multiple sources (War, Trade, Markets)
- Real market data (Forex, Crypto, Stocks, Commodities)
- AI-generated trading signals (BUY/SELL/HOLD)
- Professional Bloomberg-style UI

**Tech Stack:**
- Frontend: HTML/CSS/JS (already done by Sami)
- Backend: Python FastAPI
- APIs: Free tiers (NewsAPI, Alpha Vantage, CoinGecko, yfinance)
- Deployment: Railway (backend) + Vercel (frontend)

---

## ⚡ IMMEDIATE NEXT STEPS (Do This NOW)

### Step 1: Get API Keys (15 minutes)

Visit these sites and sign up for FREE API keys:

1. **NewsAPI** → https://newsapi.org/register
   - Click "Get API Key"
   - Free tier: 100 requests/day
   - Copy your key

2. **Alpha Vantage** → https://www.alphavantage.co/support/#api-key
   - Enter email, click "GET FREE API KEY"
   - Copy your key instantly

3. **Twelve Data** → https://twelvedata.com/pricing
   - Sign up for free
   - Get API key from dashboard
   - Free tier: 800 requests/day

4. **Supabase** (optional, for database later) → https://supabase.com/
   - Sign up
   - Create new project
   - Get database URL

**Save all keys in a text file for now**

---

### Step 2: Setup Development Environment (30 minutes)

#### On Your Local Machine:

```bash
# 1. Create project folder
mkdir trade-news-platform
cd trade-news-platform

# 2. Create backend folder
mkdir backend
cd backend

# 3. Install Python dependencies
pip install --break-system-packages fastapi uvicorn requests feedparser yfinance pandas numpy python-dotenv aiohttp

# 4. Create environment file
cat > .env << 'EOF'
NEWSAPI_KEY=paste_your_key_here
ALPHA_VANTAGE_KEY=paste_your_key_here
TWELVE_DATA_KEY=paste_your_key_here
EOF

# 5. Download the files I created
# Copy these files into backend/:
# - news_fetcher.py
# - market_data.py
# - signal_generator.py
# - main.py
```

---

### Step 3: Test Backend Locally (15 minutes)

```bash
cd backend

# Test 1: News Fetcher
python news_fetcher.py

# You should see:
# === WAR NEWS ===
# - [Real headlines from Reuters, AP, etc]
# === TRADE NEWS ===
# - [Real headlines from Bloomberg, CNBC, etc]

# Test 2: Market Data
python market_data.py

# You should see:
# Fetching Forex...
# {'symbol': 'EUR/USD', 'price': 1.08, ...}
# Fetching Crypto...
# {'symbol': 'BTC/USD', 'price': 67514.59, ...}

# Test 3: Trading Signals
python signal_generator.py

# You should see:
# EUR/USD: HOLD (Confidence: 65.0%)
#   Reasoning: RSI indicates neutral conditions. MACD shows bullish momentum.

# Test 4: Start API Server
python main.py
```

Open browser: `http://localhost:8000/docs`

You should see FastAPI Swagger UI with all endpoints.

**Try this:**
- Click on `GET /api/news/war`
- Click "Try it out"
- Click "Execute"
- You should see REAL news data in JSON format

---

### Step 4: Integrate with Frontend (30 minutes)

```bash
cd ..
mkdir frontend
cd frontend

# Copy the HTML file Sami sent
# Rename it to: index.html

# Create js folder
mkdir js

# Create js/api.js and paste the frontend-integration.js code I created

# Modify index.html
# Add this BEFORE </body>:
```

```html
<!-- Real Data Integration -->
<script>
    const API_BASE_URL = 'http://localhost:8000/api';
</script>
<script src="js/api.js"></script>
```

```bash
# Start frontend server
python3 -m http.server 8080
```

Open browser: `http://localhost:8080`

**You should see:**
- Loading overlay ("Loading real-time data...")
- Then: Real news headlines
- Real market prices
- Real trading signals

**Check browser console (F12):**
```
News loaded: {war: 10, trade: 8, markets: 12}
Markets loaded: {forex: 6, crypto: 4, stocks: 6, commodities: 3}
Signals loaded: 8
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "ModuleNotFoundError: No module named 'fastapi'"
**Fix:**
```bash
pip install --break-system-packages fastapi uvicorn requests feedparser yfinance pandas numpy python-dotenv
```

### Issue 2: "CORS error" in browser console
**Fix:** 
In `main.py`, change:
```python
allow_origins=["*"]  # Allow all origins for now
```

### Issue 3: "API key invalid"
**Fix:**
- Double-check keys in `.env`
- No spaces around `=`
- No quotes around keys
- Restart Python server after changing `.env`

### Issue 4: Data not loading in frontend
**Fix:**
1. Check backend is running (`http://localhost:8000/docs`)
2. Check browser console for errors
3. Verify `API_BASE_URL` in `js/api.js` is correct
4. Clear browser cache

---

## 📁 Project Structure (What You Should Have)

```
trade-news-platform/
├── backend/
│   ├── .env                    # Your API keys
│   ├── main.py                 # FastAPI server
│   ├── news_fetcher.py         # News aggregation
│   ├── market_data.py          # Market data
│   └── signal_generator.py     # Trading signals
└── frontend/
    ├── index.html              # Main page (from Sami)
    └── js/
        └── api.js              # API integration
```

---

## ✅ Success Checklist

After completing steps 1-4, verify:

- [ ] Backend running at `http://localhost:8000`
- [ ] API docs accessible at `http://localhost:8000/docs`
- [ ] Frontend running at `http://localhost:8080`
- [ ] Real news loading (check console)
- [ ] Real market prices displaying
- [ ] Real trading signals showing
- [ ] No errors in browser console
- [ ] No errors in terminal

---

## 🚀 Next Phase: Deployment

Once everything works locally, you'll:

1. Deploy backend to Railway (free tier)
2. Deploy frontend to Vercel (free tier)
3. Connect them together
4. Add custom domain (optional)

**Time estimate:** 2-3 hours

**Cost:** $0 (using free tiers)

---

## 📞 When to Show Sami

Show him when:
1. ✅ Everything works locally
2. ✅ Real data is loading
3. ✅ No console errors
4. ✅ Looks exactly like his demo

**What to send:**
- Screenshot of working local version
- Video screen recording showing real data loading
- Estimated deployment timeline

---

## 🎯 Current Status

You are here: **Setting up local environment**

Next milestone: **Local testing complete**

Final goal: **Deployed and live**

---

## 💡 Pro Tips

1. **Test incrementally:** Don't wait until everything is done. Test each component.

2. **Use browser DevTools:** F12 → Network tab shows all API calls

3. **Check backend logs:** Terminal running `python main.py` shows all requests

4. **Git commit often:** Save your progress
   ```bash
   git init
   git add .
   git commit -m "Backend working locally"
   ```

5. **Screenshot everything:** When it works, take screenshots for documentation

---

## 🆘 Need Help?

If stuck:
1. Check error message in terminal
2. Check browser console (F12)
3. Google the exact error message
4. Ask me specific questions with error logs

---

## ⏱️ Time Breakdown

| Task | Time |
|------|------|
| Get API keys | 15 min |
| Setup environment | 30 min |
| Test backend | 15 min |
| Integrate frontend | 30 min |
| Debug & polish | 30 min |
| **TOTAL** | **2 hours** |

---

**START NOW! 🚀**

Begin with Step 1: Get those API keys. Then come back and continue.

Good luck! You've got this! 💪
