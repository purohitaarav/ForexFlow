"""
Market data models for ForexFlow
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TrendDirection(str, Enum):
    """Trend direction enumeration"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class OHLCV(BaseModel):
    """Single candlestick data"""
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(..., ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-01T00:00:00Z",
                "open": 1.1000,
                "high": 1.1050,
                "low": 1.0950,
                "close": 1.1020,
                "volume": 1000000
            }
        }


class MarketIndicators(BaseModel):
    """Technical indicators calculated from market data"""
    returns: float
    volatility: float
    sma_20: float  # 20-period simple moving average
    sma_50: float  # 50-period simple moving average
    rsi: Optional[float] = None  # Relative Strength Index
    atr: Optional[float] = None  # Average True Range
    
    class Config:
        json_schema_extra = {
            "example": {
                "returns": 0.0015,
                "volatility": 0.0082,
                "sma_20": 1.1000,
                "sma_50": 1.0980,
                "rsi": 55.5,
                "atr": 0.0025
            }
        }


class MarketState(BaseModel):
    """
    Complete market state representation
    Used as input for MCP tools
    """
    pair: str
    current_price: float = Field(..., gt=0)
    timestamp: datetime
    historical_data: List[OHLCV]
    indicators: MarketIndicators
    
    class Config:
        json_schema_extra = {
            "example": {
                "pair": "EURUSD",
                "current_price": 1.1020,
                "timestamp": "2024-01-01T00:00:00Z",
                "historical_data": [],
                "indicators": {
                    "returns": 0.0015,
                    "volatility": 0.0082,
                    "sma_20": 1.1000,
                    "sma_50": 1.0980
                }
            }
        }


class TrendForecast(BaseModel):
    """
    Output from TrendSense MCP tool
    Probabilistic trend forecast with uncertainty
    """
    direction: TrendDirection
    confidence: float = Field(..., ge=0.0, le=1.0)
    probability_up: float = Field(..., ge=0.0, le=1.0)
    probability_down: float = Field(..., ge=0.0, le=1.0)
    probability_neutral: float = Field(..., ge=0.0, le=1.0)
    expected_move: float  # Expected price movement
    uncertainty_score: float = Field(..., ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "direction": "bullish",
                "confidence": 0.75,
                "probability_up": 0.65,
                "probability_down": 0.20,
                "probability_neutral": 0.15,
                "expected_move": 0.0025,
                "uncertainty_score": 0.25
            }
        }
