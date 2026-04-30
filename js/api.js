'use strict';

const SW_CONFIG = {
    API: 'https://bountiful-consideration-production.up.railway.app/api',
    INTERVALS: {
        signals:  60_000,   // 1 min
        markets:  30_000,   // 30 sec
        news:    300_000,   // 5 min
    },
    TTL: {
        signals:  55_000,
        markets:  25_000,
        news:    290_000,
        chart:   300_000,
    },
};

class Cache {
    constructor() { this._s = new Map(); }
    set(k, data, ttl) {
        this._s.set(k, { data, at: Date.now(), exp: Date.now() + ttl });
    }
    get(k) {
        const e = this._s.get(k);
        if (!e) return null;
        if (Date.now() > e.exp) { this._s.delete(k); return null; }
        return e;
    }
    age(k) {
        const e = this._s.get(k);
        return e ? Math.round((Date.now() - e.at) / 1000) : 0;
    }
    invalidate(k) { this._s.delete(k); }
}

class UsageTracker {
    constructor() { this._c = {}; }
    inc(svc) { this._c[svc] = (this._c[svc] || 0) + 1; }
    status(svc) { return `${this._c[svc] || 0} req`; }
}

class UpdateScheduler {
    constructor() { this._j = new Map(); }
    register(name, fn, interval) {
        if (this._j.has(name)) clearInterval(this._j.get(name));
        this._j.set(name, setInterval(fn, interval));
    }
}

async function apiFetch(url, retries = 2) {
    for (let i = 0; i <= retries; i++) {
        const ctrl = new AbortController();
        const t = setTimeout(() => ctrl.abort(), 20000);
        try {
            const res = await fetch(url, { signal: ctrl.signal });
            clearTimeout(t);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        } catch (e) {
            clearTimeout(t);
            if (e.name === 'AbortError') {
                if (i < retries) { await new Promise(r => setTimeout(r, 1500 * (i + 1))); continue; }
                throw new Error('Request timed out — backend may be starting up, try again');
            }
            if (i < retries) await new Promise(r => setTimeout(r, 1500 * (i + 1)));
            else throw e;
        }
    }
}

const _cache   = new Cache();
const _tracker = new UsageTracker();

window.SW_CONFIG  = SW_CONFIG;
window.SW_UPDATES = new UpdateScheduler();
window.SW_API = {
    cache:   _cache,
    tracker: _tracker,

    async getSentimentSignals() {
        const k = 'signals';
        const hit = _cache.get(k);
        if (hit) return { data: hit.data, fromCache: true, ageSeconds: _cache.age(k) };
        _tracker.inc('newsapi');
        const raw = await apiFetch(`${SW_CONFIG.API}/signals`);
        // Backend returns {data: [...signals array...]} — normalize into the shape loadSignals expects
        const signals = Array.isArray(raw.data) ? raw.data : (raw.data?.signals || []);
        const normalized = {
            signals,
            summary:       raw.data?.summary       || {},
            top_movers:    raw.data?.top_movers     || [],
            article_count: raw.data?.article_count  ?? signals.length,
        };
        _cache.set(k, normalized, SW_CONFIG.TTL.signals);
        return { data: normalized, fromCache: false, ageSeconds: 0 };
    },

    async getAllMarkets() {
        const cats = ['forex', 'crypto', 'stocks', 'commodities'];
        const hits = cats.map(c => _cache.get(`markets_${c}`));
        if (hits.every(Boolean)) {
            return Object.fromEntries(cats.map((c, i) => [c, hits[i].data]));
        }
        _tracker.inc('alphavantage');
        const results = await Promise.allSettled(
            cats.map(c => apiFetch(`${SW_CONFIG.API}/markets/${c}`).then(r => r.data || []))
        );
        const out = {};
        cats.forEach((c, i) => {
            const data = results[i].status === 'fulfilled' ? results[i].value : [];
            out[c] = data;
            _cache.set(`markets_${c}`, data, SW_CONFIG.TTL.markets);
        });
        return out;
    },

    async getNews(category) {
        const k = `news_${category}`;
        const hit = _cache.get(k);
        if (hit) return { data: { data: hit.data }, fromCache: true };
        _tracker.inc('newsapi');
        const raw = await apiFetch(`${SW_CONFIG.API}/news/${category}`);
        const articles = raw.data || [];
        _cache.set(k, articles, SW_CONFIG.TTL.news);
        return { data: { data: articles }, fromCache: false };
    },

    async getCryptoHistory(coinId, days) {
        const k = `chart_${coinId}_${days}`;
        const hit = _cache.get(k);
        if (hit) return { data: hit.data, fromCache: true };
        const url = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}`;
        const data = await apiFetch(url, 1);
        _cache.set(k, data, SW_CONFIG.TTL.chart);
        return { data, fromCache: false };
    },
};
