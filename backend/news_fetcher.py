"""
News Fetcher Service
Aggregates news from multiple free sources with entity-focused queries.
Sources: NewsAPI, RSS feeds, GDELT
"""
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


# NewsAPI queries — entity + topic focused for maximum signal extraction
NEWSAPI_QUERIES = {
    'war': (
        'war OR conflict OR military OR ceasefire OR invasion OR airstrike '
        'OR troops OR nato OR sanctions OR missile'
    ),
    'trade': (
        'economy OR trade OR tariff OR "trade war" OR "trade deal" OR '
        '"interest rate" OR "rate hike" OR "rate cut" OR inflation OR gdp OR recession'
    ),
    'markets': (
        'stock market OR forex OR cryptocurrency OR bitcoin OR gold OR oil OR '
        'nasdaq OR "s&p 500" OR "federal reserve" OR earnings'
    ),
    'central_banks': (
        '"federal reserve" OR powell OR ecb OR lagarde OR "bank of japan" OR '
        '"bank of england" OR "interest rates" OR "monetary policy" OR fomc'
    ),
    'crypto': (
        'bitcoin OR ethereum OR cryptocurrency OR "crypto market" OR '
        '"btc" OR "eth" OR defi OR blockchain OR sec crypto OR "crypto regulation"'
    ),
    'energy': (
        'opec OR "crude oil" OR "oil price" OR "natural gas" OR "energy crisis" '
        'OR "oil supply" OR "brent crude"'
    ),
    'tech': (
        'nvidia OR "artificial intelligence" OR "ai boom" OR semiconductor OR '
        '"big tech" OR openai OR tesla OR "tech earnings"'
    ),
}

# Free RSS feeds — no API key required
RSS_FEEDS = {
    'war': [
        'http://feeds.reuters.com/Reuters/worldNews',
        'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
        'https://feeds.bbci.co.uk/news/world/rss.xml',
    ],
    'trade': [
        'http://feeds.reuters.com/reuters/businessNews',
        'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
        'https://feeds.bbci.co.uk/news/business/rss.xml',
    ],
    'markets': [
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'https://feeds.marketwatch.com/marketwatch/topstories/',
    ],
    'central_banks': [
        'http://feeds.reuters.com/reuters/businessNews',
    ],
    'crypto': [
        'https://cointelegraph.com/rss',
        'https://decrypt.co/feed',
    ],
    'energy': [
        'http://feeds.reuters.com/reuters/businessNews',
    ],
    'tech': [
        'https://feeds.feedburner.com/TechCrunch',
        'https://www.wired.com/feed/rss',
    ],
}

URGENCY_BREAKING = ['breaking', 'urgent', 'alert', 'emergency', 'crisis', 'attack',
                    'invasion', 'crash', 'collapse']
URGENCY_DEVELOPING = ['developing', 'live', 'update', 'ongoing', 'escalat']


class NewsFetcher:

    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')

    # ── NewsAPI ───────────────────────────────────────────────────────────

    def fetch_newsapi(self, category: str = 'general') -> List[Dict]:
        if not self.newsapi_key:
            return []

        query = NEWSAPI_QUERIES.get(category, 'business news')

        params = {
            'q':        query,
            'apiKey':   self.newsapi_key,
            'language': 'en',
            'sortBy':   'publishedAt',
            'pageSize': 15,
            'from':     (datetime.now() - timedelta(hours=24)).isoformat(),
        }

        try:
            resp = requests.get('https://newsapi.org/v2/everything',
                                params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            articles = []
            for a in data.get('articles', []):
                title = a.get('title', '')
                if not title or title == '[Removed]':
                    continue
                articles.append({
                    'headline':    title,
                    'source':      a['source']['name'],
                    'category':    category,
                    'content':     a.get('description', '') or a.get('content', ''),
                    'url':         a.get('url', ''),
                    'published_at': a.get('publishedAt', datetime.now().isoformat()),
                    'urgency':     self._urgency(title),
                })
            return articles

        except Exception as e:
            print(f"NewsAPI error [{category}]: {e}")
            return []

    # ── RSS ───────────────────────────────────────────────────────────────

    def fetch_rss(self, category: str = 'general') -> List[Dict]:
        articles = []
        for url in RSS_FEEDS.get(category, []):
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:6]:
                    title = entry.get('title', '')
                    if not title:
                        continue
                    articles.append({
                        'headline':    title,
                        'source':      feed.feed.get('title', url),
                        'category':    category,
                        'content':     entry.get('summary', ''),
                        'url':         entry.get('link', ''),
                        'published_at': entry.get('published', datetime.now().isoformat()),
                        'urgency':     self._urgency(title),
                    })
            except Exception as e:
                print(f"RSS error [{url}]: {e}")
        return articles

    # ── GDELT ─────────────────────────────────────────────────────────────

    def fetch_gdelt(self, category: str = 'general') -> List[Dict]:
        query_map = {
            'war':          'war conflict military sanctions',
            'trade':        'trade tariff economy recession',
            'markets':      'stock market forex gold oil',
            'central_banks': 'federal reserve interest rates monetary policy',
            'crypto':       'bitcoin cryptocurrency blockchain',
            'energy':       'oil opec energy crude',
            'tech':         'artificial intelligence semiconductor nvidia',
        }
        query = query_map.get(category, 'business finance')

        try:
            resp = requests.get(
                'https://api.gdeltproject.org/api/v2/doc/doc',
                params={'query': query, 'mode': 'artlist',
                        'maxrecords': 8, 'format': 'json', 'sort': 'datedesc'},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            articles = []
            for a in data.get('articles', []):
                title = a.get('title', '')
                if not title:
                    continue
                articles.append({
                    'headline':    title,
                    'source':      a.get('domain', 'GDELT'),
                    'category':    category,
                    'content':     '',
                    'url':         a.get('url', ''),
                    'published_at': a.get('seendate', datetime.now().isoformat()),
                    'urgency':     self._urgency(title),
                })
            return articles

        except Exception as e:
            print(f"GDELT error [{category}]: {e}")
            return []

    # ── Aggregation ───────────────────────────────────────────────────────

    def aggregate_all(self, category: str = 'general') -> List[Dict]:
        """Fetch from all sources, deduplicate, and return sorted articles."""
        all_articles: List[Dict] = []

        if self.newsapi_key:
            all_articles.extend(self.fetch_newsapi(category))

        all_articles.extend(self.fetch_rss(category))
        all_articles.extend(self.fetch_gdelt(category))

        unique = self._deduplicate(all_articles)
        unique.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return unique[:25]

    def fetch_all_categories(self) -> List[Dict]:
        """
        Fetch news across ALL entity-relevant categories.
        Used by the sentiment signal engine to maximise entity coverage.
        """
        all_articles: List[Dict] = []
        categories = ['war', 'trade', 'markets', 'central_banks', 'crypto',
                      'energy', 'tech']

        for cat in categories:
            all_articles.extend(self.aggregate_all(cat))

        # Global deduplicate across categories
        seen: set = set()
        unique: List[Dict] = []
        for a in all_articles:
            key = a['headline'].lower().strip()[:60]
            if key not in seen:
                seen.add(key)
                unique.append(a)

        unique.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return unique[:80]

    # ── Helpers ───────────────────────────────────────────────────────────

    def _urgency(self, headline: str) -> str:
        h = headline.lower()
        if any(kw in h for kw in URGENCY_BREAKING):
            return 'BREAKING'
        if any(kw in h for kw in URGENCY_DEVELOPING):
            return 'DEVELOPING'
        return 'NEWS'

    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        seen: set = set()
        unique: List[Dict] = []
        for a in articles:
            key = a['headline'].lower().strip()[:50]
            if key not in seen:
                seen.add(key)
                unique.append(a)
        return unique
