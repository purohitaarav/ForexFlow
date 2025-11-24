"""
MCP Tool Schemas
Defines JSON input/output schemas for all MCP tools
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# PREDICT_TREND Tool (TrendSense)
# ============================================================================

class PredictTrendInput(BaseModel):
    """
    Input schema for predict_trend MCP tool
    
    This tool uses probabilistic reasoning to forecast market trends
    """
    pair: str = Field(..., description="Forex currency pair (e.g., EURUSD)")
    historical_prices: List[float] = Field(
        ..., 
        description="List of historical close prices (minimum 50 data points)",
        min_items=50
    )
    indicators: Dict[str, float] = Field(
        ...,
        description="Technical indicators (returns, volatility, sma_20, sma_50, rsi, atr)"
    )
    current_price: float = Field(..., gt=0, description="Current market price")
    timestamp: datetime = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pair": "EURUSD",
                "historical_prices": [1.1000, 1.1010, 1.1005, "..."],
                "indicators": {
                    "returns": 0.0015,
                    "volatility": 0.0082,
                    "sma_20": 1.1000,
                    "sma_50": 1.0980,
                    "rsi": 55.5,
                    "atr": 0.0025
                },
                "current_price": 1.1020,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class TrendDirection(str, Enum):
    """Trend direction enumeration"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class PredictTrendOutput(BaseModel):
    """
    Output schema for predict_trend MCP tool
    
    Returns probabilistic trend forecast with uncertainty quantification
    """
    direction: TrendDirection = Field(..., description="Predicted trend direction")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    probability_up: float = Field(..., ge=0.0, le=1.0, description="Probability of upward movement")
    probability_down: float = Field(..., ge=0.0, le=1.0, description="Probability of downward movement")
    probability_neutral: float = Field(..., ge=0.0, le=1.0, description="Probability of neutral movement")
    expected_move: float = Field(..., description="Expected price movement (absolute)")
    uncertainty_score: float = Field(..., ge=0.0, le=1.0, description="Uncertainty in prediction")
    reasoning: str = Field(..., description="Human-readable explanation of the forecast")
    
    class Config:
        json_schema_extra = {
            "example": {
                "direction": "bullish",
                "confidence": 0.75,
                "probability_up": 0.65,
                "probability_down": 0.20,
                "probability_neutral": 0.15,
                "expected_move": 0.0025,
                "uncertainty_score": 0.25,
                "reasoning": "Strong bullish trend indicated by SMA crossover and positive momentum"
            }
        }


# ============================================================================
# CHECK_CONSTRAINTS Tool (RiskGuard)
# ============================================================================

class CheckConstraintsInput(BaseModel):
    """
    Input schema for check_constraints MCP tool
    
    This tool uses CSP to validate and optimize risk parameters
    """
    pair: str = Field(..., description="Forex currency pair")
    current_price: float = Field(..., gt=0, description="Current market price")
    trend_forecast: PredictTrendOutput = Field(..., description="Trend forecast from predict_trend")
    portfolio: Dict[str, Any] = Field(
        ...,
        description="Portfolio state (capital, open_positions, total_profit_loss, max_drawdown)"
    )
    trader_profile: str = Field(
        ..., 
        description="Trader risk profile (conservative/balanced/aggressive)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pair": "EURUSD",
                "current_price": 1.1020,
                "trend_forecast": {
                    "direction": "bullish",
                    "confidence": 0.75,
                    "probability_up": 0.65,
                    "probability_down": 0.20,
                    "probability_neutral": 0.15,
                    "expected_move": 0.0025,
                    "uncertainty_score": 0.25,
                    "reasoning": "Strong bullish trend"
                },
                "portfolio": {
                    "capital": 10000.0,
                    "open_positions": 0,
                    "total_profit_loss": 0.0,
                    "max_drawdown": 0.0
                },
                "trader_profile": "balanced"
            }
        }


class CheckConstraintsOutput(BaseModel):
    """
    Output schema for check_constraints MCP tool
    
    Returns validated risk parameters from CSP solver
    """
    is_valid: bool = Field(..., description="Whether constraints are satisfied")
    max_position_size: float = Field(..., gt=0, description="Maximum allowed position size")
    stop_loss: float = Field(..., gt=0, description="Recommended stop loss price")
    take_profit: float = Field(..., gt=0, description="Recommended take profit price")
    leverage: float = Field(..., gt=0, description="Recommended leverage")
    risk_amount: float = Field(..., gt=0, description="Amount at risk (in currency)")
    risk_percentage: float = Field(..., ge=0.0, le=1.0, description="Risk as percentage of capital")
    constraint_violations: List[str] = Field(
        default_factory=list,
        description="List of constraint violations (empty if valid)"
    )
    csp_variables: Dict[str, Any] = Field(
        ...,
        description="CSP variables and their domains"
    )
    reasoning: str = Field(..., description="Explanation of constraint decisions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "max_position_size": 1000.0,
                "stop_loss": 1.0950,
                "take_profit": 1.1100,
                "leverage": 5.0,
                "risk_amount": 100.0,
                "risk_percentage": 0.01,
                "constraint_violations": [],
                "csp_variables": {
                    "position_size": {"domain": [100, 5000], "value": 1000},
                    "stop_loss_pct": {"domain": [0.005, 0.05], "value": 0.02},
                    "take_profit_pct": {"domain": [0.01, 0.10], "value": 0.04},
                    "leverage": {"domain": [1.0, 10.0], "value": 5.0}
                },
                "reasoning": "Constraints satisfied with 2:1 risk-reward ratio and 1% capital risk"
            }
        }


# ============================================================================
# FIND_BEST_TRADE Tool (OptiTrade)
# ============================================================================

class TradeActionEnum(str, Enum):
    """Trade action enumeration"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"


class FindBestTradeInput(BaseModel):
    """
    Input schema for find_best_trade MCP tool
    
    This tool uses search algorithms to find optimal trade strategy
    """
    pair: str = Field(..., description="Forex currency pair")
    current_price: float = Field(..., gt=0, description="Current market price")
    trend_forecast: PredictTrendOutput = Field(..., description="Trend forecast from predict_trend")
    risk_constraints: CheckConstraintsOutput = Field(..., description="Risk constraints from check_constraints")
    portfolio: Dict[str, Any] = Field(..., description="Portfolio state")
    search_config: Dict[str, Any] = Field(
        default_factory=lambda: {"beam_width": 5, "max_depth": 3},
        description="Search algorithm configuration"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pair": "EURUSD",
                "current_price": 1.1020,
                "trend_forecast": {
                    "direction": "bullish",
                    "confidence": 0.75,
                    "probability_up": 0.65,
                    "probability_down": 0.20,
                    "probability_neutral": 0.15,
                    "expected_move": 0.0025,
                    "uncertainty_score": 0.25,
                    "reasoning": "Strong bullish trend"
                },
                "risk_constraints": {
                    "is_valid": True,
                    "max_position_size": 1000.0,
                    "stop_loss": 1.0950,
                    "take_profit": 1.1100,
                    "leverage": 5.0,
                    "risk_amount": 100.0,
                    "risk_percentage": 0.01,
                    "constraint_violations": [],
                    "csp_variables": {},
                    "reasoning": "Constraints satisfied"
                },
                "portfolio": {
                    "capital": 10000.0,
                    "open_positions": 0,
                    "total_profit_loss": 0.0,
                    "max_drawdown": 0.0
                },
                "search_config": {
                    "beam_width": 5,
                    "max_depth": 3
                }
            }
        }


class SearchStateInfo(BaseModel):
    """Information about a search state"""
    action: TradeActionEnum
    score: float
    depth: int
    parent_state: Optional[str] = None


class FindBestTradeOutput(BaseModel):
    """
    Output schema for find_best_trade MCP tool
    
    Returns optimal trade recommendation from search algorithm
    """
    action: TradeActionEnum = Field(..., description="Recommended trade action")
    entry_price: float = Field(..., gt=0, description="Entry price for the trade")
    position_size: float = Field(..., ge=0, description="Recommended position size")
    stop_loss: float = Field(..., gt=0, description="Stop loss price")
    take_profit: float = Field(..., gt=0, description="Take profit price")
    leverage: float = Field(..., gt=0, description="Leverage to use")
    expected_profit: float = Field(..., description="Expected profit (can be negative)")
    risk_reward_ratio: float = Field(..., gt=0, description="Risk to reward ratio")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    reasoning: str = Field(..., description="Explanation of the recommendation")
    search_stats: Dict[str, Any] = Field(
        ...,
        description="Search algorithm statistics"
    )
    explored_states: List[SearchStateInfo] = Field(
        default_factory=list,
        description="States explored during search"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "buy",
                "entry_price": 1.1020,
                "position_size": 1000.0,
                "stop_loss": 1.0950,
                "take_profit": 1.1100,
                "leverage": 5.0,
                "expected_profit": 80.0,
                "risk_reward_ratio": 2.5,
                "confidence_score": 0.75,
                "reasoning": "Strong bullish trend with favorable risk-reward ratio",
                "search_stats": {
                    "states_explored": 15,
                    "beam_width_used": 5,
                    "max_depth_reached": 2,
                    "execution_time_ms": 45
                },
                "explored_states": [
                    {
                        "action": "buy",
                        "score": 0.85,
                        "depth": 0,
                        "parent_state": None
                    },
                    {
                        "action": "sell",
                        "score": 0.35,
                        "depth": 0,
                        "parent_state": None
                    }
                ]
            }
        }


# ============================================================================
# Complete MCP Pipeline Schema
# ============================================================================

class MCPPipelineInput(BaseModel):
    """
    Complete input for full MCP pipeline
    
    Runs all three tools in sequence:
    1. predict_trend
    2. check_constraints
    3. find_best_trade
    """
    pair: str
    historical_prices: List[float]
    indicators: Dict[str, float]
    current_price: float
    portfolio: Dict[str, Any]
    trader_profile: str
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPPipelineOutput(BaseModel):
    """
    Complete output from MCP pipeline
    
    Contains results from all three tools
    """
    trend_forecast: PredictTrendOutput
    risk_constraints: CheckConstraintsOutput
    trade_recommendation: FindBestTradeOutput
    pipeline_timestamp: datetime
    execution_time_ms: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "trend_forecast": {},
                "risk_constraints": {},
                "trade_recommendation": {},
                "pipeline_timestamp": "2024-01-01T00:00:00Z",
                "execution_time_ms": 125.5
            }
        }
