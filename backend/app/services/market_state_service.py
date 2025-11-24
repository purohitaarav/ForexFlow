"""
Market State Service

Builds a rich MarketState abstraction on top of raw historical data.
Computes technical indicators (returns, volatility, SMA) for downstream AI modules.
"""
import logging
from typing import List, Optional
from datetime import date
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

from app.services.historical_data_service import get_historical_data_service

logger = logging.getLogger(__name__)

class MarketState(BaseModel):
    """
    Represents the market state for a specific pair at a given point in time.
    Used by TrendSense and other modules for analysis.
    """
    pair: str
    as_of_date: date
    window_size: int
    prices: List[float] = Field(description="Ordered list of closing prices (oldest -> newest)")
    returns: List[float] = Field(description="Daily percentage returns for the window")
    volatility_20d: Optional[float] = Field(None, description="20-day rolling standard deviation of returns")
    sma_short: Optional[float] = Field(None, description="Short-term Simple Moving Average (e.g., 5-day)")
    sma_long: Optional[float] = Field(None, description="Long-term Simple Moving Average (e.g., 20-day)")
    
    # Additional metadata if needed
    data_points: int = Field(description="Number of actual data points available in window")

class MarketStateService:
    """
    Service to construct MarketState objects with computed indicators.
    """
    
    def __init__(self):
        self.data_service = get_historical_data_service()

    def get_market_state(self, pair: str, as_of_date: date, window_size: int = 60) -> MarketState:
        """
        Build a MarketState object for a pair as of a specific date.
        
        Fetches historical data window and computes:
        - Daily returns
        - 20-day Volatility (annualized or daily std dev)
        - 5-day SMA (Short)
        - 20-day SMA (Long)
        
        Args:
            pair: Currency pair symbol (e.g., 'EURUSD').
            as_of_date: The reference date for the state.
            window_size: Number of trading days to include in the history window.
            
        Returns:
            MarketState: Object containing price history and indicators.
        """
        # Ensure data is loaded
        df_all = self.data_service.load_historical_data()
        
        # Get window of data
        # We request slightly more data than window_size to compute initial returns/indicators correctly if needed,
        # but for simplicity, we'll fetch window_size + buffer (e.g. 20 for SMA)
        # Actually, get_window returns the *last* N rows ending at date.
        # To compute a 20-day SMA for the *first* point in our window, we'd need even more history.
        # However, MarketState typically represents the state *at* as_of_date, with `prices` being the recent history.
        # The indicators (SMA, Vol) are usually just needed for the *latest* point (as_of_date).
        # So we fetch enough history to compute the latest indicators.
        
        # Buffer for indicators: max(20, 5) = 20.
        # If we want a window of `window_size` prices, we fetch that.
        # But to compute SMA_20 for the *last* day, we need at least 20 days.
        # If window_size is e.g. 60, that's sufficient for SMA_20 at the end.
        
        req_window = max(window_size, 30) # Ensure we have enough for 20d calc
        
        df_window = self.data_service.get_window(df_all, pair, as_of_date, req_window)
        
        if df_window.empty:
            logger.warning(f"No data found for {pair} up to {as_of_date}")
            return MarketState(
                pair=pair,
                as_of_date=as_of_date,
                window_size=window_size,
                prices=[],
                returns=[],
                data_points=0
            )

        prices = df_window['rate'].tolist()
        
        # Compute Returns (pct_change)
        # Note: first element will be NaN in pandas, usually dropped or set to 0.
        # We'll calculate it manually or use pandas
        returns_series = df_window['rate'].pct_change().dropna()
        returns = returns_series.tolist()
        
        # Compute Indicators for the *latest* date in the window (which should be <= as_of_date)
        # 1. Volatility (20-day std dev of returns)
        if len(returns) >= 20:
            vol_20d = returns_series.tail(20).std()
        else:
            vol_20d = returns_series.std() if len(returns) > 1 else 0.0
            
        # 2. SMA Short (5-day)
        if len(prices) >= 5:
            sma_short = np.mean(prices[-5:])
        else:
            sma_short = np.mean(prices) if prices else None
            
        # 3. SMA Long (20-day)
        if len(prices) >= 20:
            sma_long = np.mean(prices[-20:])
        else:
            sma_long = np.mean(prices) if prices else None

        # Trim prices/returns to requested window_size if we fetched extra
        final_prices = prices[-window_size:]
        final_returns = returns[-(window_size-1):] if len(returns) >= window_size else returns

        return MarketState(
            pair=pair,
            as_of_date=as_of_date,
            window_size=window_size,
            prices=final_prices,
            returns=final_returns,
            volatility_20d=vol_20d,
            sma_short=sma_short,
            sma_long=sma_long,
            data_points=len(final_prices)
        )

# Singleton instance
_market_state_service = None

def get_market_state_service() -> MarketStateService:
    """Get or create the global MarketStateService instance."""
    global _market_state_service
    if _market_state_service is None:
        _market_state_service = MarketStateService()
    return _market_state_service
