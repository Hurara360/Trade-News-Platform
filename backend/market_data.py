"""
Market Data Fetcher
Uses free APIs: Alpha Vantage, Twelve Data, CoinGecko, yfinance
"""
import requests
import yfinance as yf
from datetime import datetime
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class MarketDataFetcher:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.twelve_data_key = os.getenv('TWELVE_DATA_KEY')
        
    def fetch_forex(self, symbol: str = 'EUR/USD') -> Dict:
        """
        Fetch Forex data using Alpha Vantage (25 calls/day free)
        """
        from_currency, to_currency = symbol.split('/')
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'apikey': self.alpha_vantage_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Realtime Currency Exchange Rate' in data:
                rate_data = data['Realtime Currency Exchange Rate']
                
                return {
                    'symbol': symbol,
                    'category': 'forex',
                    'price': float(rate_data['5. Exchange Rate']),
                    'bid': float(rate_data.get('8. Bid Price', rate_data['5. Exchange Rate'])),
                    'ask': float(rate_data.get('9. Ask Price', rate_data['5. Exchange Rate'])),
                    'timestamp': rate_data['6. Last Refreshed'],
                    'change_24h': 0  # Calculate separately
                }
        except Exception as e:
            print(f"Forex fetch error: {e}")
            
        # Fallback to Twelve Data
        return self._fetch_twelve_data_forex(symbol)
    
    def _fetch_twelve_data_forex(self, symbol: str) -> Dict:
        """
        Backup: Twelve Data API (800 calls/day free)
        """
        url = "https://api.twelvedata.com/quote"
        params = {
            'symbol': symbol.replace('/', ''),
            'apikey': self.twelve_data_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'price' in data:
                return {
                    'symbol': symbol,
                    'category': 'forex',
                    'price': float(data['close']),
                    'change_24h': float(data.get('percent_change', 0)),
                    'timestamp': data.get('datetime', datetime.now().isoformat())
                }
        except Exception as e:
            print(f"Twelve Data error: {e}")
            
        return None
    
    def fetch_crypto(self, symbol: str = 'BTC') -> Dict:
        """
        Fetch Crypto data using CoinGecko (50 calls/min free)
        """
        coin_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana'
        }
        
        coin_id = coin_ids.get(symbol, 'bitcoin')
        
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                coin_data = data[coin_id]
                
                return {
                    'symbol': f'{symbol}/USD',
                    'category': 'crypto',
                    'price': float(coin_data['usd']),
                    'change_24h': float(coin_data.get('usd_24h_change', 0)),
                    'volume': float(coin_data.get('usd_24h_vol', 0)),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"CoinGecko error: {e}")
            
        return None
    
    def fetch_stock(self, symbol: str = 'AAPL') -> Dict:
        """
        Fetch Stock data using yfinance (Free, Unlimited)
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            
            if current_price and previous_close:
                change_pct = ((current_price - previous_close) / previous_close) * 100
            else:
                change_pct = 0
            
            return {
                'symbol': symbol,
                'category': 'stocks',
                'price': float(current_price or 0),
                'change_24h': float(change_pct),
                'volume': float(info.get('volume', 0)),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"yfinance error for {symbol}: {e}")
            
        return None
    
    def fetch_commodity(self, symbol: str = 'GOLD') -> Dict:
        """
        Fetch Commodity data
        """
        # Map commodities to yfinance symbols
        commodity_symbols = {
            'GOLD': 'GC=F',      # Gold Futures
            'SILVER': 'SI=F',    # Silver Futures
            'CRUDE_OIL': 'CL=F', # Crude Oil Futures
            'NATURAL_GAS': 'NG=F'
        }
        
        yf_symbol = commodity_symbols.get(symbol, 'GC=F')
        
        try:
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period='2d')
            
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change_pct = ((current - previous) / previous) * 100
                
                return {
                    'symbol': symbol,
                    'category': 'commodities',
                    'price': float(current),
                    'change_24h': float(change_pct),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Commodity fetch error for {symbol}: {e}")
            
        return None
    
    def fetch_all_markets(self) -> Dict[str, List[Dict]]:
        """
        Fetch all market categories
        """
        data = {
            'forex': [],
            'crypto': [],
            'stocks': [],
            'commodities': []
        }
        
        # Forex pairs
        forex_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        for pair in forex_pairs:
            result = self.fetch_forex(pair)
            if result:
                data['forex'].append(result)
        
        # Crypto
        cryptos = ['BTC', 'ETH', 'BNB', 'SOL']
        for crypto in cryptos:
            result = self.fetch_crypto(crypto)
            if result:
                data['crypto'].append(result)
        
        # Stocks
        stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
        for stock in stocks:
            result = self.fetch_stock(stock)
            if result:
                data['stocks'].append(result)
        
        # Commodities
        commodities = ['GOLD', 'SILVER', 'CRUDE_OIL']
        for commodity in commodities:
            result = self.fetch_commodity(commodity)
            if result:
                data['commodities'].append(result)
        
        return data


# Example usage
if __name__ == "__main__":
    fetcher = MarketDataFetcher()
    
    print("Fetching Forex...")
    forex = fetcher.fetch_forex('EUR/USD')
    print(forex)
    
    print("\nFetching Crypto...")
    crypto = fetcher.fetch_crypto('BTC')
    print(crypto)
    
    print("\nFetching Stock...")
    stock = fetcher.fetch_stock('AAPL')
    print(stock)
    
    print("\nFetching Commodity...")
    commodity = fetcher.fetch_commodity('GOLD')
    print(commodity)
