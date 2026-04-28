"""
Sentiment Engine
Analyzes any text for market sentiment using weighted keyword scoring.
No external AI API needed — pure Python, zero cost.
"""
from typing import Dict, List

# Weighted bullish keywords
BULLISH: Dict[str, int] = {
    # Weight 3 — strong signal
    'surge': 3, 'soar': 3, 'skyrocket': 3, 'breakout': 3, 'all-time high': 3,
    'record high': 3, 'boom': 3, 'explode': 3, 'milestone': 3,
    # Weight 2 — medium signal
    'rally': 2, 'rise': 2, 'gain': 2, 'jump': 2, 'climb': 2, 'advance': 2,
    'growth': 2, 'recover': 2, 'rebound': 2, 'deal': 2, 'agreement': 2,
    'stimulus': 2, 'rate cut': 2, 'dovish': 2, 'easing': 2, 'approve': 2,
    'approval': 2, 'invest': 2, 'partnership': 2, 'expansion': 2, 'profit': 2,
    'bullish': 2, 'accelerate': 2, 'breakthrough': 2, 'stabilize': 2,
    'lift': 2, 'boost': 2, 'positive': 2, 'outperform': 2, 'upgrade': 2,
    'beat expectations': 3, 'better than expected': 3, 'exceeded': 2,
    # Weight 1 — light signal
    'up': 1, 'higher': 1, 'increase': 1, 'improve': 1, 'support': 1,
    'optimism': 1, 'confident': 1, 'strong': 1, 'beat': 1,
    'upside': 1, 'recover': 1, 'green': 1,
}

# Weighted bearish keywords
BEARISH: Dict[str, int] = {
    # Weight 3 — strong signal
    'crash': 3, 'collapse': 3, 'plunge': 3, 'bloodbath': 3, 'meltdown': 3,
    'crisis': 3, 'recession': 3, 'default': 3, 'bankruptcy': 3, 'bankrupt': 3,
    'invasion': 3, 'trade war': 3, 'missile': 3, 'airstrike': 3,
    'miss expectations': 3, 'worse than expected': 3,
    # Weight 2 — medium signal
    'war': 2, 'attack': 2, 'conflict': 2, 'sanctions': 2, 'ban': 2,
    'fall': 2, 'drop': 2, 'decline': 2, 'slide': 2, 'slump': 2,
    'fear': 2, 'risk': 2, 'uncertainty': 2, 'correction': 2,
    'rate hike': 2, 'hawkish': 2, 'tighten': 2, 'inflation': 2,
    'sell-off': 2, 'layoff': 2, 'downgrade': 2, 'bearish': 2,
    'tariff': 2, 'dispute': 2, 'tension': 2, 'threat': 2,
    'warning': 2, 'halt': 2, 'freeze': 2, 'block': 2, 'reject': 2,
    'downfall': 2, 'trouble': 2, 'concern': 2, 'negative': 2,
    # Weight 1 — light signal
    'down': 1, 'lower': 1, 'decrease': 1, 'pressure': 1, 'loss': 1,
    'miss': 1, 'disappoint': 1, 'underperform': 1, 'downside': 1,
    'weak': 1, 'slow': 1, 'red': 1, 'cut': 1,
}


class SentimentEngine:

    def analyze(self, text: str) -> Dict:
        """
        Score text sentiment. Returns sentiment, score (-1 to 1), confidence (0–95),
        and the keyword hits that drove the score.
        """
        text_lower = text.lower()

        bull_score = 0
        bear_score = 0
        bull_hits: List[str] = []
        bear_hits: List[str] = []

        for kw, weight in BULLISH.items():
            if kw in text_lower:
                bull_score += weight
                bull_hits.append(kw)

        for kw, weight in BEARISH.items():
            if kw in text_lower:
                bear_score += weight
                bear_hits.append(kw)

        total = bull_score + bear_score
        net   = bull_score - bear_score

        if total == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 25,
                'bullish_signals': [],
                'bearish_signals': [],
                'bull_score': 0,
                'bear_score': 0,
            }

        score      = round(net / total, 3)
        confidence = min(int(total * 11 + 25), 95)

        if score > 0.15:
            sentiment = 'bullish'
        elif score < -0.15:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'bullish_signals': bull_hits[:5],
            'bearish_signals': bear_hits[:5],
            'bull_score': bull_score,
            'bear_score': bear_score,
        }

    def batch_analyze(self, texts: List[str]) -> Dict:
        """Aggregate sentiment across multiple texts."""
        results = [self.analyze(t) for t in texts]
        if not results:
            return self.analyze('')

        avg_score = sum(r['score'] for r in results) / len(results)
        avg_conf  = int(sum(r['confidence'] for r in results) / len(results))

        if avg_score > 0.1:
            sentiment = 'bullish'
        elif avg_score < -0.1:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': round(avg_score, 3),
            'confidence': avg_conf,
            'sample_count': len(results),
        }
