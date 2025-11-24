"""
Configuration settings for ForexFlow backend
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "ForexFlow"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # MCP Tools Configuration
    MCP_TOOLS_ENABLED: bool = True
    
    # Forex API Configuration
    FOREX_API_KEY: str = "7M2SH96L7QFUYRJF"
    FOREX_API_BASE_URL: str = "https://www.alphavantage.co/query"
    FOREX_CACHE_TTL_SECONDS: int = 10
    DEBUG: bool = True
    
    # Trader Profile Configurations
    TRADER_PROFILES: dict = {
        "conservative": {
            "max_risk_per_trade": 0.01,  # 1% of capital
            "max_leverage": 2.0,
            "volatility_tolerance": "low",
            "profit_target_multiplier": 1.5,
            "max_drawdown": 0.05  # 5%
        },
        "balanced": {
            "max_risk_per_trade": 0.02,  # 2% of capital
            "max_leverage": 5.0,
            "volatility_tolerance": "medium",
            "profit_target_multiplier": 2.0,
            "max_drawdown": 0.10  # 10%
        },
        "aggressive": {
            "max_risk_per_trade": 0.05,  # 5% of capital
            "max_leverage": 10.0,
            "volatility_tolerance": "high",
            "profit_target_multiplier": 3.0,
            "max_drawdown": 0.20  # 20%
        }
    }
    
    # Market Data Configuration
    FOREX_PAIRS: List[str] = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", 
        "USDCAD", "NZDUSD", "USDCHF"
    ]
    
    # Data Pipeline Configuration
    SLIDING_WINDOW_SIZE: int = 50  # Number of candles for analysis
    MIN_CAPITAL: float = 1000.0  # Minimum account capital
    
    # TrendSense Configuration
    TREND_CONFIDENCE_THRESHOLD: float = 0.6  # 60% confidence minimum
    
    # RiskGuard Configuration
    CSP_MAX_ITERATIONS: int = 1000
    
    # OptiTrade Configuration
    SEARCH_BEAM_WIDTH: int = 5
    SEARCH_MAX_DEPTH: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
