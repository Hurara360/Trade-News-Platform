/**
 * Frontend API Integration
 * Replace the mock data in index.html with real API calls
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';  // Change in production
const UPDATE_INTERVAL = 10000; // 10 seconds

// API Client
class TradeNewsAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async fetchNews(category) {
        try {
            const response = await fetch(`${this.baseUrl}/news/${category}`);
            if (!response.ok) throw new Error('News fetch failed');
            const data = await response.json();
            return data.data;
        } catch (error) {
            console.error(`Error fetching ${category} news:`, error);
            return [];
        }
    }

    async fetchMarkets(category) {
        try {
            const response = await fetch(`${this.baseUrl}/markets/${category}`);
            if (!response.ok) throw new Error('Markets fetch failed');
            const data = await response.json();
            return data.data;
        } catch (error) {
            console.error(`Error fetching ${category} markets:`, error);
            return [];
        }
    }

    async fetchSignals() {
        try {
            const response = await fetch(`${this.baseUrl}/signals`);
            if (!response.ok) throw new Error('Signals fetch failed');
            const data = await response.json();
            return data.data;
        } catch (error) {
            console.error('Error fetching signals:', error);
            return [];
        }
    }

    async fetchAllData() {
        try {
            const response = await fetch(`${this.baseUrl}/all`);
            if (!response.ok) throw new Error('All data fetch failed');
            const data = await response.json();
            return data.data;
        } catch (error) {
            console.error('Error fetching all data:', error);
            return null;
        }
    }
}

// Initialize API client
const api = new TradeNewsAPI(API_BASE_URL);

// Data store
let liveData = {
    news: { war: [], trade: [], markets: [] },
    markets: { forex: [], crypto: [], stocks: [], commodities: [] },
    signals: []
};

// ============================================================================
// REPLACE MOCK DATA FUNCTIONS
// ============================================================================

/**
 * Load real news data
 */
async function loadRealNews() {
    try {
        const [war, trade, markets] = await Promise.all([
            api.fetchNews('war'),
            api.fetchNews('trade'),
            api.fetchNews('markets')
        ]);

        liveData.news.war = war;
        liveData.news.trade = trade;
        liveData.news.markets = markets;

        // Update newsDB global variable (used by existing code)
        newsDB.war = war.map(item => ({
            headline: item.headline,
            source: item.source,
            location: item.location || 'Global',
            urgency: { 
                text: item.urgency, 
                bg: item.urgency === 'BREAKING' ? '#C0392B' : 
                    item.urgency === 'DEVELOPING' ? '#E67E22' : '#555'
            }
        }));

        newsDB.trade = trade.map(item => ({
            headline: item.headline,
            source: item.source,
            change: '+0.87%',  // You can calculate this from sentiment
            isPositive: true
        }));

        console.log('News loaded:', { war: war.length, trade: trade.length, markets: markets.length });

    } catch (error) {
        console.error('Failed to load news:', error);
    }
}

/**
 * Load real market data
 */
async function loadRealMarkets() {
    try {
        const [forex, crypto, stocks, commodities] = await Promise.all([
            api.fetchMarkets('forex'),
            api.fetchMarkets('crypto'),
            api.fetchMarkets('stocks'),
            api.fetchMarkets('commodities')
        ]);

        liveData.markets.forex = forex;
        liveData.markets.crypto = crypto;
        liveData.markets.stocks = stocks;
        liveData.markets.commodities = commodities;

        // Update dataMap global variable
        if (forex.length > 0) {
            dataMap.forex = forex.map(item => ({
                name: item.symbol,
                price: item.price,
                change: item.change_24h || 0
            }));
        }

        if (crypto.length > 0) {
            dataMap.crypto = crypto.map(item => ({
                name: item.symbol,
                price: item.price,
                change: item.change_24h || 0
            }));
        }

        if (stocks.length > 0) {
            dataMap.stocks = stocks.map(item => ({
                name: item.symbol,
                price: item.price,
                change: item.change_24h || 0
            }));
        }

        if (commodities.length > 0) {
            dataMap.commodities = commodities.map(item => ({
                name: item.symbol,
                price: item.price,
                change: item.change_24h || 0
            }));
        }

        console.log('Markets loaded:', { forex: forex.length, crypto: crypto.length, stocks: stocks.length, commodities: commodities.length });

        // Re-render grids with real data
        ['forex', 'crypto', 'stocks', 'commodities'].forEach(renderMarketGrid);

    } catch (error) {
        console.error('Failed to load markets:', error);
    }
}

/**
 * Load real trading signals
 */
async function loadRealSignals() {
    try {
        const signals = await api.fetchSignals();
        liveData.signals = signals;

        // Update signals display
        const container = document.getElementById('signals-container');
        if (container) {
            container.innerHTML = '';
            
            signals.forEach(signal => {
                const signalElement = document.createElement('div');
                signalElement.className = 'mrow flex items-center justify-between px-4 py-2.5';
                
                const badgeClass = signal.signal_type === 'BUY' ? 'sig-buy' : 
                                   signal.signal_type === 'SELL' ? 'sig-sell' : 'sig-hold';
                
                signalElement.innerHTML = `
                    <div class="flex items-center gap-3">
                        <span class="font-mono text-sm text-white">${signal.symbol}</span>
                        <span class="text-xs text-white-dim">${signal.current_price.toFixed(2)}</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <span class="text-xs font-mono text-white-dim">${signal.confidence.toFixed(0)}%</span>
                        <span class="${badgeClass} text-xs font-bold px-3 py-1 rounded">${signal.signal_type}</span>
                    </div>
                `;
                
                container.appendChild(signalElement);
            });
        }

        console.log('Signals loaded:', signals.length);

    } catch (error) {
        console.error('Failed to load signals:', error);
    }
}

/**
 * Initialize - Load all data on page load
 */
async function initializeRealData() {
    console.log('Initializing real data...');
    
    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-overlay';
    loadingDiv.className = 'fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50';
    loadingDiv.innerHTML = `
        <div class="text-center">
            <div class="live-dot mb-4"></div>
            <p class="font-mono text-gold text-sm">Loading real-time data...</p>
        </div>
    `;
    document.body.appendChild(loadingDiv);

    try {
        // Load all data
        await Promise.all([
            loadRealNews(),
            loadRealMarkets(),
            loadRealSignals()
        ]);

        console.log('All data loaded successfully');
    } catch (error) {
        console.error('Initialization failed:', error);
    } finally {
        // Remove loading indicator
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.remove();
    }

    // Setup auto-refresh
    setInterval(async () => {
        await loadRealMarkets();  // Markets update frequently
        await loadRealSignals();   // Signals update frequently
    }, UPDATE_INTERVAL);

    // News updates less frequently (every 5 minutes)
    setInterval(async () => {
        await loadRealNews();
    }, 300000);
}

// ============================================================================
// AUTO-INITIALIZE WHEN DOM READY
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for existing code to initialize
    setTimeout(() => {
        initializeRealData();
    }, 1000);
});

console.log('Trade News API integration loaded');
