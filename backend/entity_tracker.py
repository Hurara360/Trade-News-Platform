"""
Entity Tracker
Detects market-moving entities (people, institutions, topics) in any news text.
Returns each entity with affected assets and historical directional tendencies.
"""
from typing import List, Dict

# ─────────────────────────────────────────────────────────────────────────────
# Entity definitions
# Each entry:
#   name            — canonical display name
#   aliases         — substrings to match (lowercase)
#   type            — category label
#   country         — origin / jurisdiction
#   affects         — list of asset symbols this entity moves
#   hawkish_assets  — asset → direction when entity news is BEARISH/restrictive
#   dovish_assets   — asset → direction when entity news is BULLISH/expansive
# ─────────────────────────────────────────────────────────────────────────────
ENTITIES = [

    # ── Central Banks ──────────────────────────────────────────────────────
    {
        'name': 'Federal Reserve',
        'aliases': ['federal reserve', 'fed ', 'fomc', 'jerome powell', 'powell',
                    'fed chair', 'us central bank'],
        'type': 'central_bank',
        'country': 'USA',
        'icon': '🏦',
        'affects': ['USD', 'GOLD', 'S&P 500', 'NASDAQ', 'EUR/USD', 'GBP/USD'],
        'hawkish_assets': {'USD': 'bullish', 'GOLD': 'bearish', 'S&P 500': 'bearish',
                           'NASDAQ': 'bearish', 'EUR/USD': 'bearish'},
        'dovish_assets':  {'USD': 'bearish', 'GOLD': 'bullish', 'S&P 500': 'bullish',
                           'NASDAQ': 'bullish', 'EUR/USD': 'bullish'},
    },
    {
        'name': 'ECB',
        'aliases': ['ecb', 'european central bank', 'lagarde', 'christine lagarde',
                    'eurozone rates'],
        'type': 'central_bank',
        'country': 'EU',
        'icon': '🏦',
        'affects': ['EUR/USD', 'EUR/GBP', 'GOLD', 'DAX'],
        'hawkish_assets': {'EUR/USD': 'bullish', 'GOLD': 'bearish'},
        'dovish_assets':  {'EUR/USD': 'bearish', 'GOLD': 'bullish'},
    },
    {
        'name': 'Bank of Japan',
        'aliases': ['boj', 'bank of japan', 'ueda', 'kazuo ueda', 'boj policy'],
        'type': 'central_bank',
        'country': 'Japan',
        'icon': '🏦',
        'affects': ['USD/JPY', 'EUR/JPY', 'GBP/JPY'],
        'hawkish_assets': {'USD/JPY': 'bearish'},
        'dovish_assets':  {'USD/JPY': 'bullish'},
    },
    {
        'name': 'Bank of England',
        'aliases': ['boe', 'bank of england', 'andrew bailey', 'bailey'],
        'type': 'central_bank',
        'country': 'UK',
        'icon': '🏦',
        'affects': ['GBP/USD', 'EUR/GBP'],
        'hawkish_assets': {'GBP/USD': 'bullish'},
        'dovish_assets':  {'GBP/USD': 'bearish'},
    },
    {
        'name': 'PBoC',
        'aliases': ['pboc', "people's bank of china", 'chinese central bank',
                    'china rate', 'china stimulus'],
        'type': 'central_bank',
        'country': 'China',
        'icon': '🏦',
        'affects': ['AUD/USD', 'COPPER', 'CRUDE OIL', 'USD/CNH'],
        'hawkish_assets': {'AUD/USD': 'bearish', 'COPPER': 'bearish'},
        'dovish_assets':  {'AUD/USD': 'bullish', 'COPPER': 'bullish'},
    },

    # ── Political Leaders ──────────────────────────────────────────────────
    {
        'name': 'Donald Trump',
        'aliases': ['donald trump', 'trump', 'mar-a-lago', 'trump administration',
                    'trump tariff', 'truth social'],
        'type': 'politician',
        'country': 'USA',
        'icon': '🏛️',
        'affects': ['USD', 'S&P 500', 'NASDAQ', 'GOLD', 'CRUDE OIL', 'BTC/USD',
                    'EUR/USD', 'COPPER'],
        'hawkish_assets': {'USD': 'mixed', 'S&P 500': 'bearish', 'GOLD': 'bullish',
                           'CRUDE OIL': 'bullish'},
        'dovish_assets':  {'USD': 'bullish', 'S&P 500': 'bullish', 'GOLD': 'bearish'},
    },
    {
        'name': 'Joe Biden',
        'aliases': ['joe biden', 'biden administration', 'white house', 'president biden'],
        'type': 'politician',
        'country': 'USA',
        'icon': '🏛️',
        'affects': ['USD', 'S&P 500', 'NASDAQ', 'CRUDE OIL'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
    {
        'name': 'Xi Jinping',
        'aliases': ['xi jinping', 'chinese president', 'beijing stimulus',
                    'china government', 'cpc', 'communist party'],
        'type': 'politician',
        'country': 'China',
        'icon': '🏛️',
        'affects': ['AUD/USD', 'COPPER', 'CRUDE OIL', 'S&P 500', 'USD/CNH'],
        'hawkish_assets': {'AUD/USD': 'bearish', 'COPPER': 'bearish', 'S&P 500': 'bearish'},
        'dovish_assets':  {'AUD/USD': 'bullish', 'COPPER': 'bullish', 'S&P 500': 'bullish'},
    },
    {
        'name': 'Vladimir Putin',
        'aliases': ['vladimir putin', 'putin', 'kremlin', 'russia government',
                    'russian president'],
        'type': 'politician',
        'country': 'Russia',
        'icon': '🏛️',
        'affects': ['CRUDE OIL', 'BRENT', 'GOLD', 'EUR/USD', 'NAT GAS'],
        'hawkish_assets': {'CRUDE OIL': 'bullish', 'BRENT': 'bullish',
                           'GOLD': 'bullish', 'EUR/USD': 'bearish'},
        'dovish_assets':  {'CRUDE OIL': 'bearish', 'GOLD': 'bearish'},
    },
    {
        'name': 'Narendra Modi',
        'aliases': ['narendra modi', 'modi', 'india government', 'new delhi policy'],
        'type': 'politician',
        'country': 'India',
        'icon': '🏛️',
        'affects': ['USD/INR', 'GOLD'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },

    # ── Tech & Business Leaders ────────────────────────────────────────────
    {
        'name': 'Elon Musk',
        'aliases': ['elon musk', 'musk', '@elonmusk', 'x corp', 'xai',
                    'tesla ceo', 'spacex'],
        'type': 'tech_leader',
        'country': 'USA',
        'icon': '💡',
        'affects': ['DOGE/USD', 'BTC/USD', 'TSLA', 'S&P 500'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
    {
        'name': 'Michael Saylor',
        'aliases': ['michael saylor', 'saylor', 'microstrategy'],
        'type': 'crypto_influencer',
        'country': 'USA',
        'icon': '₿',
        'affects': ['BTC/USD'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
    {
        'name': 'Sam Altman',
        'aliases': ['sam altman', 'openai', 'chatgpt', 'gpt-5'],
        'type': 'tech_leader',
        'country': 'USA',
        'icon': '💡',
        'affects': ['NVDA', 'MSFT', 'NASDAQ'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
    {
        'name': 'Warren Buffett',
        'aliases': ['warren buffett', 'buffett', 'berkshire hathaway'],
        'type': 'investor',
        'country': 'USA',
        'icon': '📈',
        'affects': ['S&P 500', 'AAPL', 'GOLD'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },

    # ── Organizations & Regulators ─────────────────────────────────────────
    {
        'name': 'OPEC',
        'aliases': ['opec', 'opec+', 'saudi aramco', 'mbs', 'mohammed bin salman',
                    'saudi oil', 'oil cartel'],
        'type': 'organization',
        'country': 'Global',
        'icon': '🛢️',
        'affects': ['CRUDE OIL', 'BRENT', 'NAT GAS', 'USD', 'S&P 500'],
        'hawkish_assets': {'CRUDE OIL': 'bullish', 'BRENT': 'bullish',
                           'NAT GAS': 'bullish'},
        'dovish_assets':  {'CRUDE OIL': 'bearish', 'BRENT': 'bearish'},
    },
    {
        'name': 'SEC',
        'aliases': ['sec ', 'securities and exchange', 'gary gensler', 'gensler',
                    'sec crypto', 'sec ruling'],
        'type': 'regulator',
        'country': 'USA',
        'icon': '⚖️',
        'affects': ['BTC/USD', 'ETH/USD', 'SOL/USD', 'NASDAQ'],
        'hawkish_assets': {'BTC/USD': 'bearish', 'ETH/USD': 'bearish',
                           'SOL/USD': 'bearish', 'NASDAQ': 'bearish'},
        'dovish_assets':  {'BTC/USD': 'bullish', 'ETH/USD': 'bullish'},
    },
    {
        'name': 'IMF / World Bank',
        'aliases': ['imf', 'international monetary fund', 'world bank',
                    'imf forecast', 'imf warning'],
        'type': 'institution',
        'country': 'Global',
        'icon': '🌐',
        'affects': ['USD', 'GOLD', 'S&P 500', 'EM currencies'],
        'hawkish_assets': {'USD': 'bearish', 'GOLD': 'bullish'},
        'dovish_assets':  {'USD': 'bullish', 'GOLD': 'bearish'},
    },
    {
        'name': 'NATO',
        'aliases': ['nato', 'north atlantic', 'nato summit', 'nato forces'],
        'type': 'organization',
        'country': 'Global',
        'icon': '🛡️',
        'affects': ['GOLD', 'CRUDE OIL', 'EUR/USD', 'USD'],
        'hawkish_assets': {'GOLD': 'bullish', 'CRUDE OIL': 'bullish',
                           'EUR/USD': 'bearish'},
        'dovish_assets':  {'GOLD': 'bearish'},
    },
    {
        'name': 'US Treasury',
        'aliases': ['us treasury', 'janet yellen', 'yellen', 'treasury yield',
                    'treasury bonds', 'bond market'],
        'type': 'institution',
        'country': 'USA',
        'icon': '🏛️',
        'affects': ['USD', 'GOLD', 'S&P 500'],
        'hawkish_assets': {'USD': 'bullish', 'GOLD': 'bearish'},
        'dovish_assets':  {'USD': 'bearish', 'GOLD': 'bullish'},
    },

    # ── Economic Indicators (treated as entities) ──────────────────────────
    {
        'name': 'US Inflation (CPI)',
        'aliases': ['inflation', 'cpi', 'pce', 'consumer price index',
                    'core inflation', 'price index'],
        'type': 'economic_data',
        'country': 'USA',
        'icon': '📊',
        'affects': ['GOLD', 'USD', 'S&P 500', 'NASDAQ'],
        'hawkish_assets': {'GOLD': 'bullish', 'USD': 'mixed', 'S&P 500': 'bearish'},
        'dovish_assets':  {'GOLD': 'bearish', 'S&P 500': 'bullish'},
    },
    {
        'name': 'US Jobs / Employment',
        'aliases': ['nonfarm payroll', 'non-farm payroll', 'jobs report',
                    'unemployment rate', 'jobless claims', 'payroll data',
                    'labor market'],
        'type': 'economic_data',
        'country': 'USA',
        'icon': '📊',
        'affects': ['USD', 'S&P 500', 'GOLD', 'EUR/USD'],
        'hawkish_assets': {'USD': 'bullish', 'GOLD': 'bearish', 'S&P 500': 'bullish'},
        'dovish_assets':  {'USD': 'bearish', 'GOLD': 'bullish', 'S&P 500': 'bearish'},
    },
    {
        'name': 'GDP Data',
        'aliases': ['gdp', 'gross domestic product', 'economic growth',
                    'gdp growth', 'economic output'],
        'type': 'economic_data',
        'country': 'Global',
        'icon': '📊',
        'affects': ['USD', 'S&P 500', 'NASDAQ', 'CRUDE OIL'],
        'hawkish_assets': {'USD': 'bullish', 'S&P 500': 'bullish'},
        'dovish_assets':  {'USD': 'bearish', 'S&P 500': 'bearish'},
    },

    # ── Macro Themes ───────────────────────────────────────────────────────
    {
        'name': 'Geopolitical Conflict',
        'aliases': ['war', 'ceasefire', 'military operation', 'airstrike',
                    'troops deploy', 'armed conflict', 'missile strike',
                    'military tension', 'naval', 'siege'],
        'type': 'geopolitical',
        'country': 'Global',
        'icon': '⚔️',
        'affects': ['GOLD', 'CRUDE OIL', 'BRENT', 'USD', 'S&P 500', 'BTC/USD'],
        'hawkish_assets': {'GOLD': 'bullish', 'CRUDE OIL': 'bullish',
                           'BRENT': 'bullish', 'USD': 'bullish',
                           'S&P 500': 'bearish'},
        'dovish_assets':  {'GOLD': 'bearish', 'S&P 500': 'bullish',
                           'CRUDE OIL': 'bearish'},
    },
    {
        'name': 'Trade War / Tariffs',
        'aliases': ['tariff', 'trade war', 'import duty', 'trade deficit',
                    'protectionism', 'trade barrier', 'trade deal', 'trade agreement'],
        'type': 'trade_policy',
        'country': 'Global',
        'icon': '🌍',
        'affects': ['USD', 'S&P 500', 'COPPER', 'AUD/USD', 'CNH'],
        'hawkish_assets': {'USD': 'mixed', 'S&P 500': 'bearish',
                           'COPPER': 'bearish', 'AUD/USD': 'bearish'},
        'dovish_assets':  {'S&P 500': 'bullish', 'COPPER': 'bullish',
                           'AUD/USD': 'bullish'},
    },
    {
        'name': 'Crypto / Blockchain',
        'aliases': ['bitcoin', 'btc', 'ethereum', 'eth', 'cryptocurrency',
                    'blockchain', 'defi', 'web3', 'nft', 'crypto market',
                    'digital asset', 'stablecoin', 'altcoin'],
        'type': 'asset_class',
        'country': 'Global',
        'icon': '₿',
        'affects': ['BTC/USD', 'ETH/USD', 'SOL/USD', 'BNB/USD', 'DOGE/USD'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
    {
        'name': 'Energy / Oil',
        'aliases': ['crude oil', 'brent crude', 'oil price', 'energy crisis',
                    'oil supply', 'oil demand', 'petroleum', 'natural gas'],
        'type': 'commodity',
        'country': 'Global',
        'icon': '⛽',
        'affects': ['CRUDE OIL', 'BRENT', 'NAT GAS', 'USD', 'S&P 500'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
    {
        'name': 'Gold / Precious Metals',
        'aliases': ['gold price', 'gold demand', 'gold rally', 'safe haven gold',
                    'bullion', 'silver price', 'precious metals'],
        'type': 'commodity',
        'country': 'Global',
        'icon': '🥇',
        'affects': ['GOLD', 'SILVER', 'PLATINUM'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
    {
        'name': 'Tech Sector',
        'aliases': ['artificial intelligence', 'ai boom', 'semiconductor',
                    'chip shortage', 'nvidia earnings', 'tech earnings',
                    'big tech', 'silicon valley'],
        'type': 'sector',
        'country': 'USA',
        'icon': '💻',
        'affects': ['NASDAQ', 'NVDA', 'AAPL', 'MSFT', 'GOOGL'],
        'hawkish_assets': {},
        'dovish_assets':  {},
    },
]


class EntityTracker:

    def extract(self, text: str) -> List[Dict]:
        """
        Extract all market-moving entities from a text string.
        Returns list of matched entities with their asset impact maps.
        """
        text_lower = text.lower()
        found: List[Dict] = []
        seen_names: set = set()

        for entity in ENTITIES:
            for alias in entity['aliases']:
                if alias in text_lower and entity['name'] not in seen_names:
                    found.append({
                        'name':            entity['name'],
                        'type':            entity['type'],
                        'country':         entity['country'],
                        'icon':            entity.get('icon', '◆'),
                        'affects':         entity['affects'],
                        'hawkish_assets':  entity.get('hawkish_assets', {}),
                        'dovish_assets':   entity.get('dovish_assets', {}),
                        'matched_alias':   alias.strip(),
                    })
                    seen_names.add(entity['name'])
                    break

        return found

    def top_movers(self, articles: list, top_n: int = 8) -> List[Dict]:
        """
        Rank entities by mention frequency across a list of articles.
        Returns top N entities with mention count and average sentiment.
        """
        from collections import defaultdict
        counts: Dict = defaultdict(lambda: {'count': 0, 'entity': None})

        for article in articles:
            text = f"{article.get('headline', '')} {article.get('content', '')}"
            for entity in self.extract(text):
                name = entity['name']
                counts[name]['count'] += 1
                counts[name]['entity'] = entity

        ranked = sorted(counts.values(), key=lambda x: x['count'], reverse=True)
        return [
            {**r['entity'], 'mentions': r['count']}
            for r in ranked[:top_n]
            if r['entity']
        ]
