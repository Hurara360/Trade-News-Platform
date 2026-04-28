"""
Asset Mapper
Combines entity detection + sentiment to produce structured trading signals.
Each signal includes the full reasoning chain: news → entity → asset → direction.
"""
from typing import List, Dict
from datetime import datetime


SIGNAL_MAP = {'bullish': 'BUY', 'bearish': 'SELL', 'hold': 'HOLD', 'neutral': 'HOLD'}

REASON_TEMPLATES = {
    'central_bank': {
        'bullish': "{name} signals dovish shift — supports risk assets, pressures safe-havens",
        'bearish': "{name} signals hawkish stance — rate expectations tighten liquidity",
        'neutral': "{name} holds steady — markets await clearer policy direction",
    },
    'politician': {
        'bullish': "Positive political development involving {name} — markets react favourably",
        'bearish': "Political risk from {name} — uncertainty weighs on sentiment",
        'neutral': "{name} statement noted — market impact unclear",
    },
    'tech_leader': {
        'bullish': "{name} positive news — investor confidence in tech/crypto elevated",
        'bearish': "{name} concern — sentiment-linked assets under pressure",
        'neutral': "{name} activity monitored — directional bias inconclusive",
    },
    'crypto_influencer': {
        'bullish': "{name} bullish stance fuels crypto inflows",
        'bearish': "{name} bearish comments pressure digital assets",
        'neutral': "{name} neutral — crypto market awaits catalyst",
    },
    'investor': {
        'bullish': "{name} bullish signal — institutional confidence rising",
        'bearish': "{name} cautionary signal — smart money reducing exposure",
        'neutral': "{name} activity noted — no clear directional bias",
    },
    'organization': {
        'bullish': "{name} positive action — supply/demand balance improves",
        'bearish': "{name} restrictive action — supply concerns weigh on prices",
        'neutral': "{name} holds steady — watch for follow-through",
    },
    'regulator': {
        'bullish': "{name} approves / eases — regulatory clarity unlocks flows",
        'bearish': "{name} tightens / bans — regulatory headwind suppresses prices",
        'neutral': "{name} reviewing — markets in wait-and-see mode",
    },
    'institution': {
        'bullish': "{name} positive assessment — confidence in global outlook improves",
        'bearish': "{name} issues warning — downside risks flagged globally",
        'neutral': "{name} maintains outlook — no significant revision",
    },
    'economic_data': {
        'bullish': "{name} beats expectations — supports risk-on positioning",
        'bearish': "{name} disappoints — recession/slowdown fears resurface",
        'neutral': "{name} in-line — limited market reaction expected",
    },
    'geopolitical': {
        'bullish': "Geopolitical de-escalation — risk assets benefit, safe-havens retreat",
        'bearish': "Geopolitical escalation — safe-haven demand surges, risk assets sell off",
        'neutral': "Geopolitical situation monitored — no decisive shift in risk premium",
    },
    'trade_policy': {
        'bullish': "Trade deal / easing — global growth outlook improves",
        'bearish': "Trade restrictions / tariffs — growth headwind for exposed assets",
        'neutral': "Trade talks ongoing — markets cautious on outcome",
    },
    'asset_class': {
        'bullish': "Direct {name} positive news — sector-wide momentum building",
        'bearish': "Direct {name} negative news — sector-wide selling pressure",
        'neutral': "{name} news noted — no strong directional bias",
    },
    'commodity': {
        'bullish': "{name} supply tightens / demand rises — price support confirmed",
        'bearish': "{name} demand falls / supply rises — price pressure building",
        'neutral': "{name} market balanced — range-bound likely",
    },
    'sector': {
        'bullish': "{name} sector momentum — capital rotation into related assets",
        'bearish': "{name} sector headwinds — risk reduction in related assets",
        'neutral': "{name} sector mixed — no dominant trend",
    },
}


class AssetMapper:

    def generate_signals(
        self,
        entities: List[Dict],
        sentiment: Dict,
        headline: str,
        source: str = '',
        article_url: str = '',
        published_at: str = '',
        urgency: str = 'NEWS',
    ) -> List[Dict]:
        """
        For each entity found in the article, map to affected assets and
        generate a trading signal with full reasoning chain.
        """
        signals: List[Dict] = []
        sentiment_type = sentiment['sentiment']   # bullish | bearish | neutral
        confidence_base = sentiment['confidence']

        for entity in entities:
            etype = entity['type']

            # Pick the directional asset map based on sentiment
            if sentiment_type == 'bearish':
                asset_map = entity.get('hawkish_assets', {})
            elif sentiment_type == 'bullish':
                asset_map = entity.get('dovish_assets', {})
            else:
                asset_map = {}

            reason = self._build_reason(entity, sentiment_type)

            if asset_map:
                for asset, direction in asset_map.items():
                    if direction == 'mixed':
                        direction = 'hold'
                    signals.append(self._make_signal(
                        asset=asset,
                        direction=direction,
                        confidence=confidence_base,
                        entity=entity,
                        reason=reason,
                        headline=headline,
                        source=source,
                        article_url=article_url,
                        published_at=published_at,
                        urgency=urgency,
                    ))
            else:
                # No directional map — apply raw sentiment to top 3 affected assets
                for asset in entity['affects'][:3]:
                    direction = sentiment_type if sentiment_type != 'neutral' else 'hold'
                    signals.append(self._make_signal(
                        asset=asset,
                        direction=direction,
                        confidence=max(confidence_base - 15, 25),
                        entity=entity,
                        reason=reason,
                        headline=headline,
                        source=source,
                        article_url=article_url,
                        published_at=published_at,
                        urgency=urgency,
                    ))

        return signals

    # ── helpers ───────────────────────────────────────────────────────────

    def _make_signal(
        self, asset, direction, confidence, entity, reason,
        headline, source, article_url, published_at, urgency
    ) -> Dict:
        return {
            'asset':        asset,
            'signal':       SIGNAL_MAP.get(direction, 'HOLD'),
            'direction':    direction,
            'confidence':   min(int(confidence), 95),
            'entity':       entity['name'],
            'entity_type':  entity['type'],
            'entity_icon':  entity.get('icon', '◆'),
            'entity_country': entity.get('country', ''),
            'reason':       reason,
            'headline':     headline,
            'source':       source,
            'article_url':  article_url,
            'published_at': published_at or datetime.now().isoformat(),
            'urgency':      urgency,
            'generated_at': datetime.now().isoformat(),
        }

    def _build_reason(self, entity: Dict, sentiment: str) -> str:
        etype = entity['type']
        name  = entity['name']
        templates = REASON_TEMPLATES.get(etype, {
            'bullish': f"{name} positive news — markets react favourably",
            'bearish': f"{name} negative news — markets react cautiously",
            'neutral': f"{name} activity noted — await further clarity",
        })
        template = templates.get(sentiment, templates.get('neutral', ''))
        return template.format(name=name)
