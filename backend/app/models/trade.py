"""
Trade models for ForexFlow
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TradeAction(str, Enum):
    """Trade action types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"


class TraderProfile(str, Enum):
    """Trader profile types"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class Portfolio(BaseModel):
    """User portfolio state"""
    capital: float = Field(..., gt=0)
    open_positions: int = Field(default=0, ge=0)
    total_profit_loss: float = Field(default=0.0)
    max_drawdown: float = Field(default=0.0, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "capital": 10000.0,
                "open_positions": 2,
                "total_profit_loss": 150.50,
                "max_drawdown": 0.03
            }
        }


class RiskConstraints(BaseModel):
    """
    Output from RiskGuard MCP tool
    CSP-validated trade constraints
    """
    max_position_size: float = Field(..., ge=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    leverage: float = Field(..., ge=0)
    risk_amount: float = Field(..., ge=0)
    is_valid: bool
    constraint_violations: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "max_position_size": 1000.0,
                "stop_loss": 1.0950,
                "take_profit": 1.1100,
                "leverage": 5.0,
                "risk_amount": 100.0,
                "is_valid": True,
                "constraint_violations": []
            }
        }


class TradeRecommendation(BaseModel):
    """
    Output from OptiTrade MCP tool
    Search-based optimal trade recommendation
    """
    action: TradeAction
    pair: str
    entry_price: float = Field(..., gt=0)
    position_size: float = Field(..., ge=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    leverage: float = Field(..., gt=0)
    expected_profit: float
    risk_reward_ratio: float = Field(..., ge=0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "buy",
                "pair": "EURUSD",
                "entry_price": 1.1020,
                "position_size": 1000.0,
                "stop_loss": 1.0950,
                "take_profit": 1.1100,
                "leverage": 5.0,
                "expected_profit": 80.0,
                "risk_reward_ratio": 2.5,
                "confidence_score": 0.75,
                "reasoning": "Strong bullish trend with low volatility"
            }
        }


class TradeRequest(BaseModel):
    """Request model for trade recommendation endpoint"""
    pair: str
    trader_profile: TraderProfile = TraderProfile.BALANCED
    capital: float = Field(..., gt=0)
    current_positions: int = Field(default=0, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "pair": "EURUSD",
                "trader_profile": "balanced",
                "capital": 10000.0,
                "current_positions": 0
            }
        }


class TradeResponse(BaseModel):
    """Complete response from orchestrator"""
    recommendation: TradeRecommendation
    trend_forecast: dict
    risk_constraints: RiskConstraints
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendation": {
                    "action": "buy",
                    "pair": "EURUSD",
                    "entry_price": 1.1020,
                    "position_size": 1000.0,
                    "stop_loss": 1.0950,
                    "take_profit": 1.1100,
                    "leverage": 5.0,
                    "expected_profit": 80.0,
                    "risk_reward_ratio": 2.5,
                    "confidence_score": 0.75,
                    "reasoning": "Strong bullish trend"
                },
                "trend_forecast": {},
                "risk_constraints": {},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
