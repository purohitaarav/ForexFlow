"""
Trade recommendation router
Handles the main trade recommendation endpoint using MCP orchestration
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.models.trade import Portfolio, TraderProfile
from app.core.orchestrator import orchestrator
from app.core.config import settings
from app.services.market_service import MarketService

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.get("/recommend_trade")
async def recommend_trade(
    pair: str = Query(..., description="Forex currency pair (e.g., EURUSD)"),
    profile: str = Query("balanced", description="Trader profile: conservative, balanced, or aggressive"),
    capital: float = Query(10000.0, gt=0, description="Available capital"),
    open_positions: int = Query(0, ge=0, description="Number of open positions"),
    market_service: MarketService = Depends(),
):
    """
    Get AI-powered trade recommendation
    
    This endpoint orchestrates all three MCP tools:
    1. Fetches live market data (or uses fallback)
    2. TrendSense → Analyzes market trends probabilistically
    3. OptiTrade → Generates optimal trade strategies using beam search
    4. RiskGuard → Validates constraints using CSP
    
    Args:
        pair: Forex currency pair (e.g., EURUSD, GBPUSD)
        profile: Trader risk profile (conservative/balanced/aggressive)
        capital: Available trading capital
        open_positions: Number of currently open positions
        
    Returns:
        Unified response with:
        - trend: Probabilistic trend forecast
        - strategy: Optimal trade strategy from beam search
        - risk_analysis: CSP-validated risk constraints
        - final_recommendation: Actionable trade recommendation
        - explanation: Human-readable explanation
        
    Example:
        GET /api/recommend_trade?pair=EURUSD&profile=conservative&capital=10000
    """
    pair_upper = pair.upper()

    # Validate pair
    if pair_upper not in settings.FOREX_PAIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported forex pair. Supported pairs: {', '.join(settings.FOREX_PAIRS)}"
        )
    
    # Validate and parse trader profile
    try:
        trader_profile = TraderProfile(profile.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trader profile. Must be one of: conservative, balanced, aggressive"
        )
    
    # Create portfolio
    portfolio = Portfolio(
        capital=capital,
        open_positions=open_positions,
        total_profit_loss=0.0,
        max_drawdown=0.0
    )
    
    try:
        # Fetch market state
        market_state = await market_service.get_market_state(pair.upper())

        # Run MCP orchestration pipeline
        recommendation = await orchestrator.recommend_trade(
            market_state=market_state,
            portfolio=portfolio,
            trader_profile=trader_profile
        )
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendation: {str(e)}"
        )


@router.get("/recommend_trade/batch")
async def recommend_trade_batch(
    pairs: str = Query(..., description="Comma-separated forex pairs (e.g., EURUSD,GBPUSD)"),
    profile: str = Query("balanced", description="Trader profile"),
    capital: float = Query(10000.0, gt=0, description="Available capital"),
    market_service: MarketService = Depends(),
):
    """
    Get trade recommendations for multiple pairs
    
    Runs the MCP pipeline for each pair and returns all recommendations.
    
    Args:
        pairs: Comma-separated list of forex pairs
        profile: Trader risk profile
        capital: Available trading capital
        
    Returns:
        Dictionary mapping each pair to its recommendation
        
    Example:
        GET /api/recommend_trade/batch?pairs=EURUSD,GBPUSD&profile=aggressive
    """
    # Parse pairs
    pair_list = [p.strip().upper() for p in pairs.split(",")]
    
    # Validate pairs
    invalid_pairs = [p for p in pair_list if p not in settings.FOREX_PAIRS]
    if invalid_pairs:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported pairs: {', '.join(invalid_pairs)}"
        )
    
    # Validate trader profile
    try:
        trader_profile = TraderProfile(profile.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trader profile. Must be one of: conservative, balanced, aggressive"
        )
    
    # Create portfolio
    portfolio = Portfolio(
        capital=capital,
        open_positions=0,
        total_profit_loss=0.0,
        max_drawdown=0.0
    )
    
    try:
        # Get recommendations for all pairs
        # market_service is already injected via Depends()
        
        recommendations = {}
        for pair in pair_list:
            try:
                market_state = await market_service.get_market_state(pair)
                recommendation = await orchestrator.recommend_trade(
                    market_state=market_state,
                    portfolio=portfolio,
                    trader_profile=trader_profile
                )
                recommendations[pair] = recommendation
            except Exception as e:
                # Log error and continue with other pairs
                recommendations[pair] = {"error": str(e)}
        
        return {
            "pairs": pair_list,
            "profile": profile,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating batch recommendations: {str(e)}"
        )
