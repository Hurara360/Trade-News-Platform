"""
Database Models for Trade News Platform
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class NewsItem(Base):
    """Store news articles"""
    __tablename__ = "news_items"
    
    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String(500), nullable=False)
    source = Column(String(100))
    category = Column(String(50))  # 'war', 'trade', 'markets'
    location = Column(String(200))
    urgency = Column(String(20))  # 'BREAKING', 'DEVELOPING', 'NEWS'
    content = Column(Text)
    url = Column(String(500))
    published_at = Column(DateTime, default=datetime.utcnow)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Sentiment analysis results
    sentiment_score = Column(Float)  # -1 to 1
    market_impact = Column(JSON)  # {BTC: +2.5%, GOLD: +1.2%, etc}
    

class MarketPrice(Base):
    """Store real-time market prices"""
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)  # 'BTC/USD', 'EUR/USD'
    category = Column(String(20))  # 'forex', 'crypto', 'stocks', 'commodities'
    price = Column(Float, nullable=False)
    change_24h = Column(Float)  # Percentage change
    volume = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    

class TradingSignal(Base):
    """Store generated trading signals"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal_type = Column(String(10))  # 'BUY', 'SELL', 'HOLD'
    confidence = Column(Float)  # 0-100
    
    # Technical indicators
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    
    # Price levels
    support_1 = Column(Float)
    support_2 = Column(Float)
    resistance_1 = Column(Float)
    resistance_2 = Column(Float)
    
    reasoning = Column(Text)  # Why this signal was generated
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class CachedData(Base):
    """Cache API responses to reduce API calls"""
    __tablename__ = "cached_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(200), unique=True, index=True)
    data = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
