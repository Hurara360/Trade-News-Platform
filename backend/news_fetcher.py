"""
News Fetcher Service
Aggregates news from multiple free sources
"""
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class NewsFetcher:
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        
    def fetch_newsapi(self, category: str = 'general') -> List[Dict]:
        """
        Fetch from NewsAPI.org (100 requests/day free)
        """
        if not self.newsapi_key:
            return []
            
        # Map categories to NewsAPI queries
        queries = {
            'war': 'war OR conflict OR military OR ceasefire',
            'trade': 'economy OR trade OR market OR fed OR interest rate',
            'markets': 'stock market OR forex OR crypto OR commodities'
        }
        
        query = queries.get(category, 'business')
        
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': self.newsapi_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 10,
            'from': (datetime.now() - timedelta(hours=24)).isoformat()
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'headline': article['title'],
                    'source': article['source']['name'],
                    'category': category,
                    'content': article.get('description', ''),
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'urgency': self._determine_urgency(article['title'])
                })
            
            return articles
            
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []
    
    def fetch_rss_feeds(self, category: str = 'general') -> List[Dict]:
        """
        Fetch from RSS feeds (Unlimited, Free)
        """
        feeds = {
            'war': [
                'http://feeds.reuters.com/Reuters/worldNews',
                'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'
            ],
            'trade': [
                'http://feeds.reuters.com/reuters/businessNews',
                'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml'
            ],
            'markets': [
                'http://feeds.reuters.com/news/wealth',
                'https://www.cnbc.com/id/100003114/device/rss/rss.html'
            ]
        }
        
        articles = []
        
        for feed_url in feeds.get(category, []):
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Top 5 from each feed
                    articles.append({
                        'headline': entry.get('title', ''),
                        'source': feed.feed.get('title', 'RSS Feed'),
                        'category': category,
                        'content': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'published_at': entry.get('published', datetime.now().isoformat()),
                        'urgency': self._determine_urgency(entry.get('title', ''))
                    })
                    
            except Exception as e:
                print(f"RSS feed error ({feed_url}): {e}")
                continue
        
        return articles
    
    def fetch_gdelt(self, category: str = 'general') -> List[Dict]:
        """
        Fetch from GDELT Project (Free, Real-time global news)
        """
        # GDELT API endpoint
        base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        
        queries = {
            'war': 'war conflict military',
            'trade': 'trade economy market',
            'markets': 'stock market forex crypto'
        }
        
        query = queries.get(category, 'business')
        
        params = {
            'query': query,
            'mode': 'artlist',
            'maxrecords': 10,
            'format': 'json',
            'sort': 'datedesc'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'headline': article.get('title', ''),
                    'source': article.get('domain', 'GDELT'),
                    'category': category,
                    'content': article.get('seendate', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('seendate', datetime.now().isoformat()),
                    'urgency': self._determine_urgency(article.get('title', ''))
                })
            
            return articles
            
        except Exception as e:
            print(f"GDELT error: {e}")
            return []
    
    def aggregate_all(self, category: str = 'general') -> List[Dict]:
        """
        Aggregate from all sources
        """
        all_articles = []
        
        # Try NewsAPI first (if key exists)
        if self.newsapi_key:
            all_articles.extend(self.fetch_newsapi(category))
        
        # Always fetch RSS (free, unlimited)
        all_articles.extend(self.fetch_rss_feeds(category))
        
        # Add GDELT
        all_articles.extend(self.fetch_gdelt(category))
        
        # Remove duplicates based on headline similarity
        unique_articles = self._deduplicate(all_articles)
        
        # Sort by published date
        unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return unique_articles[:20]  # Return top 20
    
    def _determine_urgency(self, headline: str) -> str:
        """Determine urgency level from headline"""
        headline_lower = headline.lower()
        
        breaking_keywords = ['breaking', 'urgent', 'alert', 'emergency', 'crisis']
        developing_keywords = ['developing', 'live', 'update', 'ongoing']
        
        if any(kw in headline_lower for kw in breaking_keywords):
            return 'BREAKING'
        elif any(kw in headline_lower for kw in developing_keywords):
            return 'DEVELOPING'
        else:
            return 'NEWS'
    
    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on headline similarity"""
        seen = set()
        unique = []
        
        for article in articles:
            headline_normalized = article['headline'].lower().strip()[:50]
            if headline_normalized not in seen:
                seen.add(headline_normalized)
                unique.append(article)
        
        return unique


# Example usage
if __name__ == "__main__":
    fetcher = NewsFetcher()
    
    # Test all categories
    for category in ['war', 'trade', 'markets']:
        print(f"\n=== {category.upper()} NEWS ===")
        articles = fetcher.aggregate_all(category)
        for article in articles[:3]:
            print(f"- {article['headline']} ({article['source']})")
