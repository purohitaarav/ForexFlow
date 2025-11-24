/**
 * API Service for ForexFlow Frontend
 * 
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TradeRecommendation {
    action: string;
    pair: string;
    entry_price: number;
    position_size: number;
    stop_loss: number;
    take_profit: number;
    leverage: number;
    expected_profit: number;
    risk_reward_ratio: number;
    confidence_score: number;
    reasoning: string;
}

export interface TrendForecast {
    direction: string;
    confidence: number;
    probability_up: number;
    probability_down: number;
    probability_neutral: number;
    expected_move: number;
    uncertainty_score: number;
}

export interface RiskConstraints {
    max_position_size: number;
    stop_loss: number;
    take_profit: number;
    leverage: number;
    risk_amount: number;
    is_valid: boolean;
    constraint_violations: string[];
}

export interface TradeResponse {
    recommendation: TradeRecommendation;
    trend_forecast: TrendForecast;
    risk_constraints: RiskConstraints;
    timestamp: string;
}

export interface MarketData {
    pair: string;
    current_price: number;
    timestamp: string;
    indicators: {
        returns: number;
        volatility: number;
        sma_20: number;
        sma_50: number;
        rsi?: number;
        atr?: number;
    };
}

/**
 * Get trade recommendation from AI
 */
export async function getTradeRecommendation(
    pair: string,
    traderProfile: string = 'balanced',
    capital: number = 10000
): Promise<TradeResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/recommend_trade?pair=${pair}&trader_profile=${traderProfile}&capital=${capital}`
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get recommendation');
    }

    return response.json();
}

/**
 * Get current market data
 */
export async function getMarketData(pair: string): Promise<MarketData> {
    const response = await fetch(`${API_BASE_URL}/api/market_data/${pair}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get market data');
    }

    return response.json();
}

/**
 * Get trader profiles
 */
export async function getTraderProfiles() {
    const response = await fetch(`${API_BASE_URL}/api/trader_profiles`);

    if (!response.ok) {
        throw new Error('Failed to get trader profiles');
    }

    return response.json();
}

/**
 * Get MCP tools status
 */
export async function getMCPToolsStatus() {
    const response = await fetch(`${API_BASE_URL}/api/mcp_tools/status`);

    if (!response.ok) {
        throw new Error('Failed to get MCP tools status');
    }

    return response.json();
}

/**
 * Health check
 */
export async function healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
        throw new Error('API health check failed');
    }

    return response.json();
}
