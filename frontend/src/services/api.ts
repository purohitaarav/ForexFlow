/**
 * API Service for ForexFlow Frontend
 * 
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TrendForecast {
    direction: string;
    confidence: number;
    probability_up: number;
    probability_down: number;
    probability_neutral: number;
    expected_move: number;
    uncertainty_score: number;
}

export interface RiskAnalysis {
    is_valid: boolean;
    max_position_size: number;
    risk_amount: number;
    constraint_violations: string[];
}

export interface Strategy {
    action: string;
    entry_price: number;
    position_size: number;
    stop_loss: number;
    take_profit: number;
    leverage: number;
    expected_profit: number;
    risk_reward_ratio: number;
    confidence_score: number;
}

export interface FinalRecommendation {
    action: string;
    pair: string;
    trader_profile: string;
    timestamp: string;
}

export interface MarketData {
    pair: string;
    current_price: number;
    volatility: number;
}

// New unified response from orchestrator
export interface TradeResponse {
    trend: TrendForecast;
    strategy: Strategy;
    risk_analysis: RiskAnalysis;
    final_recommendation: FinalRecommendation;
    explanation: string;
    market_data: MarketData;
}

/**
 * Get trade recommendation from AI orchestrator
 */
export async function getTradeRecommendation(
    pair: string,
    traderProfile: string = 'balanced',
    capital: number = 10000
): Promise<TradeResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/recommend_trade?pair=${pair}&profile=${traderProfile}&capital=${capital}`
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
 * Get live quote for a pair
 */
export async function getLiveQuote(pair: string) {
    const response = await fetch(`${API_BASE_URL}/api/market/test_live_quote?pair=${pair}`);

    if (!response.ok) {
        throw new Error('Failed to get live quote');
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

// Historical Data Interfaces
export interface MarketState {
    pair: string;
    as_of_date: string;
    window_size: number;
    prices: number[];
    returns: number[];
    volatility_20d: number | null;
    sma_short: number | null;
    sma_long: number | null;
    data_points: number;
}

export interface TrendAnalysisResponse {
    pair: string;
    as_of_date: string;
    trend_up_prob: number;
    trend_down_prob: number;
    volatility: number;
    explanation: string;
}

/**
 * Get historical market state
 */
export async function getHistoricalState(
    pair: string,
    date: string,
    windowSize: number = 60
): Promise<MarketState> {
    const response = await fetch(
        `${API_BASE_URL}/api/historical_state?pair=${pair}&date=${date}&window_size=${windowSize}`
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get historical market state');
    }

    return response.json();
}

/**
 * Get historical trend analysis
 */
export async function getTrendAnalysis(
    pair: string,
    date: string,
    windowSize: number = 60
): Promise<TrendAnalysisResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/trend_analysis?pair=${pair}&date=${date}&window_size=${windowSize}`
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get trend analysis');
    }

    return response.json();
}
