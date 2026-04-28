"""
Trading Signal Generator
Generates BUY/SELL/HOLD signals using real technical indicators
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class SignalGenerator:
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """
        Calculate RSI (Relative Strength Index)
        Returns value between 0-100
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def calculate_macd(self, prices: pd.Series) -> Dict:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return {
            'macd': macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0,
            'signal': signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0,
            'histogram': (macd - signal).iloc[-1] if not pd.isna((macd - signal).iloc[-1]) else 0
        }
    
    def calculate_support_resistance(self, prices: pd.Series) -> Dict:
        """
        Calculate support and resistance levels using pivot points
        """
        high = prices.max()
        low = prices.min()
        close = prices.iloc[-1]
        
        pivot = (high + low + close) / 3
        
        resistance_1 = (2 * pivot) - low
        resistance_2 = pivot + (high - low)
        
        support_1 = (2 * pivot) - high
        support_2 = pivot - (high - low)
        
        return {
            'pivot': pivot,
            'resistance_1': resistance_1,
            'resistance_2': resistance_2,
            'support_1': support_1,
            'support_2': support_2
        }
    
    def generate_signal(self, symbol: str, category: str = 'forex') -> Dict:
        """
        Generate trading signal for a given symbol
        """
        try:
            # Map symbols to yfinance tickers
            ticker_map = {
                'EUR/USD': 'EURUSD=X',
                'GBP/USD': 'GBPUSD=X',
                'BTC/USD': 'BTC-USD',
                'ETH/USD': 'ETH-USD',
                'GOLD': 'GC=F',
                'CRUDE_OIL': 'CL=F',
                'S&P_500': '^GSPC',
                'NASDAQ': '^IXIC'
            }
            
            yf_symbol = ticker_map.get(symbol, symbol)
            
            # Fetch historical data (30 days)
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period='30d')
            
            if len(hist) < 20:
                return self._default_signal(symbol)
            
            prices = hist['Close']
            
            # Calculate indicators
            rsi = self.calculate_rsi(prices)
            macd_data = self.calculate_macd(prices)
            sr_levels = self.calculate_support_resistance(prices)
            
            current_price = prices.iloc[-1]
            
            # Generate signal based on indicators
            signal_type = self._determine_signal(rsi, macd_data, current_price, sr_levels)
            confidence = self._calculate_confidence(rsi, macd_data)
            reasoning = self._generate_reasoning(signal_type, rsi, macd_data)
            
            return {
                'symbol': symbol,
                'signal_type': signal_type,
                'confidence': confidence,
                'current_price': float(current_price),
                'rsi': float(rsi),
                'macd': float(macd_data['macd']),
                'macd_signal': float(macd_data['signal']),
                'support_1': float(sr_levels['support_1']),
                'support_2': float(sr_levels['support_2']),
                'resistance_1': float(sr_levels['resistance_1']),
                'resistance_2': float(sr_levels['resistance_2']),
                'reasoning': reasoning,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Signal generation error for {symbol}: {e}")
            return self._default_signal(symbol)
    
    def _determine_signal(self, rsi: float, macd_data: Dict, price: float, sr: Dict) -> str:
        """
        Determine BUY/SELL/HOLD based on indicators
        """
        signals = []
        
        # RSI signals
        if rsi < 30:  # Oversold
            signals.append('BUY')
        elif rsi > 70:  # Overbought
            signals.append('SELL')
        else:
            signals.append('HOLD')
        
        # MACD signals
        if macd_data['macd'] > macd_data['signal'] and macd_data['histogram'] > 0:
            signals.append('BUY')
        elif macd_data['macd'] < macd_data['signal'] and macd_data['histogram'] < 0:
            signals.append('SELL')
        else:
            signals.append('HOLD')
        
        # Support/Resistance signals
        if price <= sr['support_1']:
            signals.append('BUY')  # Near support, potential bounce
        elif price >= sr['resistance_1']:
            signals.append('SELL')  # Near resistance, potential reversal
        
        # Majority vote
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            return 'BUY'
        elif sell_count > buy_count:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_confidence(self, rsi: float, macd_data: Dict) -> float:
        """
        Calculate confidence score (0-100)
        """
        confidence = 50.0  # Base confidence
        
        # RSI contribution
        if rsi < 30 or rsi > 70:
            confidence += 20  # Strong RSI signal
        elif 40 < rsi < 60:
            confidence -= 10  # Neutral RSI
        
        # MACD contribution
        macd_strength = abs(macd_data['histogram'])
        if macd_strength > 0.5:
            confidence += 15
        elif macd_strength > 0.2:
            confidence += 10
        
        # Cap confidence
        return min(max(confidence, 0), 100)
    
    def _generate_reasoning(self, signal: str, rsi: float, macd_data: Dict) -> str:
        """
        Generate human-readable reasoning
        """
        reasons = []
        
        if rsi < 30:
            reasons.append("RSI indicates oversold conditions")
        elif rsi > 70:
            reasons.append("RSI indicates overbought conditions")
        
        if macd_data['histogram'] > 0:
            reasons.append("MACD shows bullish momentum")
        elif macd_data['histogram'] < 0:
            reasons.append("MACD shows bearish momentum")
        
        if not reasons:
            reasons.append("Indicators suggest neutral market conditions")
        
        return ". ".join(reasons) + "."
    
    def _default_signal(self, symbol: str) -> Dict:
        """
        Return default HOLD signal when data unavailable
        """
        return {
            'symbol': symbol,
            'signal_type': 'HOLD',
            'confidence': 50.0,
            'current_price': 0.0,
            'rsi': 50.0,
            'macd': 0.0,
            'macd_signal': 0.0,
            'support_1': 0.0,
            'support_2': 0.0,
            'resistance_1': 0.0,
            'resistance_2': 0.0,
            'reasoning': 'Insufficient data for signal generation',
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_all_signals(self) -> List[Dict]:
        """
        Generate signals for all major symbols
        """
        symbols = [
            ('EUR/USD', 'forex'),
            ('GBP/USD', 'forex'),
            ('BTC/USD', 'crypto'),
            ('ETH/USD', 'crypto'),
            ('GOLD', 'commodities'),
            ('CRUDE_OIL', 'commodities'),
            ('S&P_500', 'stocks'),
            ('NASDAQ', 'stocks')
        ]
        
        signals = []
        for symbol, category in symbols:
            signal = self.generate_signal(symbol, category)
            signals.append(signal)
        
        return signals


# Example usage
if __name__ == "__main__":
    generator = SignalGenerator()
    
    print("Generating signals...")
    signals = generator.generate_all_signals()
    
    for signal in signals:
        print(f"\n{signal['symbol']}: {signal['signal_type']} "
              f"(Confidence: {signal['confidence']:.1f}%)")
        print(f"  Reasoning: {signal['reasoning']}")
        print(f"  RSI: {signal['rsi']:.2f} | MACD: {signal['macd']:.4f}")
