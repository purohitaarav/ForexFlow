"""
Historical Data Router

Exposes endpoints for querying historical market state and running
TrendSense analysis on historical data.
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Dict, Any

from app.services.market_state_service import get_market_state_service
from app.mcp_tools.trend_sense import create_trend_sense_tool

router = APIRouter(prefix="/api", tags=["historical"])

@router.get("/historical_state")
async def get_historical_state(
    pair: str = Query(..., description="Currency pair, e.g., EURUSD"),
    as_of_date: str = Query(..., description="Date in YYYY-MM-DD format", alias="date"),
    window_size: int = Query(60, ge=10, le=365, description="Lookback window size in days")
):
    """
    Get the market state (prices, indicators) for a specific pair and date.
    
    Returns:
        MarketState object containing price history, returns, volatility, and SMAs.
    """
    try:
        # Parse date
        try:
            target_date = datetime.strptime(as_of_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        service = get_market_state_service()
        state = service.get_market_state(pair, target_date, window_size)

        if state.data_points == 0:
             raise HTTPException(status_code=404, detail=f"No historical data found for {pair} on or before {as_of_date}")

        return state

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving market state: {str(e)}")

@router.get("/trend_analysis")
async def get_trend_analysis(
    pair: str = Query(..., description="Currency pair, e.g., EURUSD"),
    as_of_date: str = Query(..., description="Date in YYYY-MM-DD format", alias="date"),
    window_size: int = Query(60, ge=10, le=365, description="Lookback window size in days")
):
    """
    Run TrendSense analysis on historical data for a specific date.
    
    Returns:
        Trend prediction including probabilities, direction, and explanation.
    """
    try:
        # Parse date
        try:
            target_date = datetime.strptime(as_of_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Check data availability first
        service = get_market_state_service()
        state = service.get_market_state(pair, target_date, window_size)
        
        if state.data_points == 0:
             raise HTTPException(status_code=404, detail=f"No historical data found for {pair} on or before {as_of_date}")

        # Run analysis
        tool = create_trend_sense_tool()
        result = tool.predict_trend(pair, target_date, window_size)
        
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running trend analysis: {str(e)}")
