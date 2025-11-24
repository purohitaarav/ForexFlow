"""
API Routes for ForexFlow
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import numpy as np

from app.models.trade import (
    TradeRequest, TradeResponse, Portfolio, TraderProfile
)
from app.models.market import MarketState, MarketIndicators, OHLCV
from app.core.orchestrator import orchestrator
from app.core.config import settings

router = APIRouter()


@router.get("/recommend_trade")
async def recommend_trade(
    pair: str = Query(..., description="Forex pair (e.g., EURUSD)"),
    trader_profile: str = Query("balanced", description="Trader profile: conservative, balanced, or aggressive"),
    capital: float = Query(10000.0, description="Available capital", gt=0)
) -> TradeResponse:
    """
    Get AI-powered trade recommendation
    
    This endpoint orchestrates all three MCP tools:
    1. TrendSense - Probabilistic trend forecast
    2. RiskGuard - Risk constraint validation
    3. OptiTrade - Optimal trade strategy search
    
    Args:
        pair: Forex currency pair
        trader_profile: Risk profile (conservative/balanced/aggressive)
        capital: Available trading capital
        
    Returns:
        Complete trade recommendation with analysis
    """
    # Validate inputs
    if pair not in settings.FOREX_PAIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported forex pair. Supported pairs: {settings.FOREX_PAIRS}"
        )
    
    try:
        profile = TraderProfile(trader_profile.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid trader profile. Must be: conservative, balanced, or aggressive"
        )
    
    # TODO: Fetch real market data from data source
    # For now, generate mock market state
    market_state = await _get_market_state(pair)
    
    # Create portfolio
    portfolio = Portfolio(
        capital=capital,
        open_positions=0,
        total_profit_loss=0.0,
        max_drawdown=0.0
    )
    
    # Get recommendation from orchestrator
    try:
        recommendation = await orchestrator.recommend_trade(
            market_state=market_state,
            portfolio=portfolio,
            trader_profile=profile
        )
        return recommendation
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendation: {str(e)}"
        )


@router.get("/market_data/{pair}")
async def get_market_data(pair: str):
    """
    Get current market data for a forex pair
    
    Args:
        pair: Forex currency pair
        
    Returns:
        Current market state with indicators
    """
    if pair not in settings.FOREX_PAIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported forex pair. Supported pairs: {settings.FOREX_PAIRS}"
        )
    
    market_state = await _get_market_state(pair)
    return market_state


@router.get("/trader_profiles")
async def get_trader_profiles():
    """
    Get available trader profiles and their configurations
    
    Returns:
        Dictionary of trader profiles with parameters
    """
    return {
        "profiles": settings.TRADER_PROFILES,
        "description": {
            "conservative": "Low risk, low volatility tolerance, suitable for risk-averse traders",
            "balanced": "Moderate risk, balanced approach for most traders",
            "aggressive": "High risk, profit-focused for experienced traders"
        }
    }


@router.get("/mcp_tools/status")
async def get_mcp_tools_status():
    """
    Get status of all MCP tools
    
    Returns:
        Status of TrendSense, RiskGuard, and OptiTrade
    """
    return orchestrator.get_tool_status()


# Helper functions

async def _get_market_state(pair: str) -> MarketState:
    """
    Get current market state for a forex pair
    
    TODO: Replace with real data source (e.g., Alpha Vantage, Yahoo Finance)
    Currently returns mock data for demonstration
    """
    # Mock current price
    base_prices = {
        "EURUSD": 1.1000,
        "GBPUSD": 1.2500,
        "USDJPY": 110.00,
        "AUDUSD": 0.7500,
        "USDCAD": 1.2500,
        "NZDUSD": 0.7000,
        "USDCHF": 0.9200
    }
    
    current_price = base_prices.get(pair, 1.0000)
    
    # Add some random variation
    current_price *= (1 + np.random.uniform(-0.005, 0.005))
    
    # Mock historical data (last 50 candles)
    historical_data = []
    price = current_price
    
    for i in range(50):
        # Random walk
        change = np.random.uniform(-0.002, 0.002)
        open_price = price
        close_price = price * (1 + change)
        high_price = max(open_price, close_price) * (1 + abs(np.random.uniform(0, 0.001)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.uniform(0, 0.001)))
        
        candle = OHLCV(
            timestamp=datetime.now(),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=np.random.uniform(100000, 1000000)
        )
        historical_data.append(candle)
        price = close_price
    
    # Calculate indicators
    closes = np.array([c.close for c in historical_data])
    returns = np.diff(closes) / closes[:-1]
    
    indicators = MarketIndicators(
        returns=float(np.mean(returns)),
        volatility=float(np.std(returns)),
        sma_20=float(np.mean(closes[-20:])),
        sma_50=float(np.mean(closes[-50:])),
        rsi=50.0 + np.random.uniform(-20, 20),  # Mock RSI
        atr=float(np.std(closes[-14:]) * 0.01)  # Mock ATR
    )
    
    return MarketState(
        pair=pair,
        current_price=current_price,
        timestamp=datetime.now(),
        historical_data=historical_data,
        indicators=indicators
    )
