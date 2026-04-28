"""
Sentiment-Based Signal Generator
Converts news articles → entity detection → sentiment → trading signals.
Replaces old candlestick/RSI-only approach.
"""
from typing import List, Dict
from datetime import datetime
from sentiment_engine import SentimentEngine
from entity_tracker import EntityTracker
from asset_mapper import AssetMapper


class SignalGenerator:

    def __init__(self):
        self.sentiment = SentimentEngine()
        self.entities  = EntityTracker()
        self.mapper    = AssetMapper()

    # ── Public API ────────────────────────────────────────────────────────

    def process_article(self, article: Dict) -> List[Dict]:
        """Process a single article and return its trading signals."""
        text = f"{article.get('headline', '')} {article.get('content', '')}"

        sentiment_result = self.sentiment.analyze(text)
        entity_list      = self.entities.extract(text)

        if not entity_list:
            return []

        signals = self.mapper.generate_signals(
            entities    = entity_list,
            sentiment   = sentiment_result,
            headline    = article.get('headline', ''),
            source      = article.get('source', ''),
            article_url = article.get('url', ''),
            published_at= article.get('published_at', ''),
            urgency     = article.get('urgency', 'NEWS'),
        )

        # Attach raw sentiment data for UI
        for sig in signals:
            sig['sentiment_score']    = sentiment_result['score']
            sig['bullish_keywords']   = sentiment_result.get('bullish_signals', [])
            sig['bearish_keywords']   = sentiment_result.get('bearish_signals', [])

        return signals

    def generate_from_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process a list of articles and return deduplicated, confidence-ranked signals.
        """
        all_signals: List[Dict] = []
        seen: set = set()

        for article in articles:
            for sig in self.process_article(article):
                # Deduplicate by asset + signal direction + headline snippet
                key = f"{sig['asset']}|{sig['signal']}|{sig['headline'][:50]}"
                if key not in seen:
                    seen.add(key)
                    all_signals.append(sig)

        # Sort: high confidence first, then most recent
        all_signals.sort(
            key=lambda x: (x['confidence'], x['generated_at']),
            reverse=True
        )
        return all_signals[:60]

    def generate_all_signals(self) -> List[Dict]:
        """
        Compatibility shim — called by old main.py routes.
        Returns empty list; real call is generate_from_articles().
        """
        return []

    def get_summary(self, signals: List[Dict]) -> Dict:
        """Aggregate statistics over a signal list."""
        if not signals:
            return {
                'total': 0, 'buy': 0, 'sell': 0, 'hold': 0,
                'top_assets': [], 'top_entities': [],
                'market_bias': 'neutral', 'avg_confidence': 0,
            }

        buy  = sum(1 for s in signals if s['signal'] == 'BUY')
        sell = sum(1 for s in signals if s['signal'] == 'SELL')
        hold = sum(1 for s in signals if s['signal'] == 'HOLD')
        avg_conf = int(sum(s['confidence'] for s in signals) / len(signals))

        # Top assets by signal count
        asset_counts: Dict[str, int] = {}
        for s in signals:
            asset_counts[s['asset']] = asset_counts.get(s['asset'], 0) + 1
        top_assets = sorted(asset_counts.items(), key=lambda x: x[1], reverse=True)[:6]

        # Top entities by mention
        entity_counts: Dict[str, int] = {}
        entity_meta: Dict[str, Dict] = {}
        for s in signals:
            name = s['entity']
            entity_counts[name] = entity_counts.get(name, 0) + 1
            entity_meta[name] = {
                'name': name,
                'type': s['entity_type'],
                'icon': s.get('entity_icon', '◆'),
            }
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:8]

        if buy > sell * 1.4:
            bias = 'bullish'
        elif sell > buy * 1.4:
            bias = 'bearish'
        else:
            bias = 'neutral'

        return {
            'total':          len(signals),
            'buy':            buy,
            'sell':           sell,
            'hold':           hold,
            'avg_confidence': avg_conf,
            'market_bias':    bias,
            'top_assets':     [{'asset': a, 'count': c} for a, c in top_assets],
            'top_entities':   [
                {**entity_meta[n], 'mentions': c}
                for n, c in top_entities
                if n in entity_meta
            ],
        }
