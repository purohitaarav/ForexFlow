"""
Market data router
Handles market data and analysis endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List

from app.models.market import MarketState, OHLCV
from app.services.market_service import MarketService
from app.core.config import settings

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/data/{pair}", response_model=MarketState)
async def get_market_data(
    pair: str,
    market_service: MarketService = Depends()
) -> MarketState:
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
            detail=f"Unsupported forex pair. Supported: {settings.FOREX_PAIRS}"
        )
    
    try:
        market_state = await market_service.get_market_state(pair)
        return market_state
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching market data: {str(e)}"
        )


@router.get("/historical/{pair}")
async def get_historical_data(
    pair: str,
    timeframe: str = Query("1d", description="Timeframe (currently daily CSV data)"),
    limit: int = Query(100, ge=1, le=1000),
    market_service: MarketService = Depends()
) -> List[OHLCV]:
    """
    Get historical OHLCV data sourced from the CSV dataset.
    """
    if pair not in settings.FOREX_PAIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported forex pair. Supported: {settings.FOREX_PAIRS}"
        )

    try:
        data = await market_service.get_historical_data(pair, timeframe=timeframe, limit=limit)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")


@router.get("/indicators/{pair}")
async def get_technical_indicators(
    pair: str,
    indicators: str = Query("sma,rsi,atr", description="Comma-separated indicator list"),
    market_service: MarketService = Depends()
):
    """
    Get technical indicators for a pair
    
    TODO: Implement technical indicator calculations
    - SMA (Simple Moving Average)
    - EMA (Exponential Moving Average)
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - ATR (Average True Range)
    
    Args:
        pair: Forex currency pair
        indicators: Comma-separated list of indicators
        
    Returns:
        Dictionary of indicator values
    """
    # TODO: Implement indicator calculations
    raise HTTPException(
        status_code=501,
        detail="Technical indicators not yet implemented"
    )


@router.get("/pairs")
async def get_supported_pairs():
    """
    Get list of supported forex pairs
    
    Returns:
        List of supported currency pairs
    """
    return {
        "pairs": settings.FOREX_PAIRS,
        "count": len(settings.FOREX_PAIRS)
    }


@router.get("/live_quote")
async def get_live_quote(
    pair: str = Query(..., description="Forex pair to fetch (e.g. EURUSD)"),
    market_service: MarketService = Depends()
):
    """Return the most recent quote derived from the historical CSV data."""
    if pair not in settings.FOREX_PAIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported forex pair. Supported: {settings.FOREX_PAIRS}"
        )

    try:
        quote = await market_service.get_latest_quote(pair)
        return quote
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quote: {str(e)}")


@router.get("/volatility/{pair}")
async def get_volatility_analysis(
    pair: str,
    period: int = Query(20, ge=5, le=200),
    market_service: MarketService = Depends()
):
    """
    Get volatility analysis for a pair
    
    TODO: Implement volatility calculations
    - Historical volatility
    - Implied volatility (if options data available)
    - Volatility percentile
    - ATR-based volatility
    
    Args:
        pair: Forex currency pair
        period: Lookback period for calculation
        
    Returns:
        Volatility metrics
    """
    # TODO: Implement volatility analysis
    raise HTTPException(
        status_code=501,
        detail="Volatility analysis not yet implemented"
    )


@router.get("/test_live_quote")
async def test_live_quote(
    pair: str = Query("EURUSD", description="Forex pair to fetch"),
    market_service: MarketService = Depends()
):
    """Test endpoint that returns the latest CSV-derived quote."""
    if pair not in settings.FOREX_PAIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported forex pair. Supported: {settings.FOREX_PAIRS}"
        )

    try:
        quote = await market_service.get_latest_quote(pair)
        return {
            "success": True,
            "data": quote,
            "cached": True  # Data comes from CSV cache
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live quote: {str(e)}")

