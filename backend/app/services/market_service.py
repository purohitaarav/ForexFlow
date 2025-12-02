"""
Market Service
Business logic for market data retrieval and analysis
"""
import numpy as np
import logging
from typing import List

from app.models.market import MarketState, OHLCV, MarketIndicators
from app.services.historical_data_service import get_historical_data_service

logger = logging.getLogger(__name__)


class MarketService:
    """
    Service layer for market data operations
    
    Handles:
    - Market data retrieval
    - Technical indicator calculation
    - Historical data management
    - Data caching
    """
    
    def __init__(self):
        self._historical_service = get_historical_data_service()
    
    async def get_market_state(self, pair: str) -> MarketState:
        """
        Get current market state for a forex pair using historical CSV data.
        
        Args:
            pair: Forex currency pair
            
        Returns:
            Current market state with indicators
        """
        from app.services.historical_data_service import get_historical_data_service
        
        hist_service = get_historical_data_service()
        df = hist_service.load_historical_data()
        
        # Get history for pair
        pair_df = hist_service.get_pair_history(df, pair)
        
        if pair_df.empty:
            raise ValueError(f"No historical data found for {pair} in CSV")
            
        # Convert to OHLCV
        # Since CSV only has daily rates, we use the rate for O/H/L/C
        historical_data = []
        for date_idx, row in pair_df.iterrows():
            price = float(row['rate'])
            candle = OHLCV(
                timestamp=date_idx,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=0.0
            )
            historical_data.append(candle)
            
        if len(historical_data) < 50:
            raise ValueError("Insufficient historical data to compute indicators")

        indicators = await self.calculate_indicators(historical_data)

        latest_candle = historical_data[-1]

        return MarketState(
            pair=pair,
            current_price=latest_candle.close,
            timestamp=latest_candle.timestamp,
            historical_data=historical_data[-100:], # Keep last 100 candles
            indicators=indicators
        )
    
    async def get_historical_data(
        self,
        pair: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> List[OHLCV]:
        """
        Get historical OHLCV data
        
        TODO: Implement real data fetching
        - Connect to data source API
        - Support multiple timeframes
        - Cache results for performance
        - Handle rate limiting
        
        Args:
            pair: Forex currency pair
            timeframe: Candlestick timeframe
            limit: Number of candles to return
            
        Returns:
            List of OHLCV candles
        """
        historical_data = self._load_pair_history(pair)

        if not historical_data:
            raise ValueError(f"No historical data available for {pair}")

        return historical_data[-limit:]
    
    async def calculate_indicators(
        self,
        historical_data: List[OHLCV]
    ) -> MarketIndicators:
        """
        Calculate technical indicators from historical data
        
        Args:
            historical_data: List of OHLCV candles
            
        Returns:
            Calculated market indicators
        """
        if len(historical_data) < 50:
            raise ValueError("Insufficient data for indicator calculation")
        
        # Extract close prices
        closes = np.array([candle.close for candle in historical_data])
        highs = np.array([candle.high for candle in historical_data])
        lows = np.array([candle.low for candle in historical_data])
        
        # Calculate returns
        returns = np.diff(closes) / closes[:-1]
        avg_return = float(np.mean(returns))
        
        # Calculate volatility (standard deviation of returns)
        volatility = float(np.std(returns))
        
        # Calculate Simple Moving Averages
        sma_20 = float(np.mean(closes[-20:]))
        sma_50 = float(np.mean(closes[-50:]))
        
        # Calculate RSI
        rsi = self._calculate_rsi(closes, period=14)
        
        # Calculate ATR (Average True Range)
        atr = self._calculate_atr(highs, lows, closes, period=14)
        
        return MarketIndicators(
            returns=avg_return,
            volatility=volatility,
            sma_20=sma_20,
            sma_50=sma_50,
            rsi=rsi,
            atr=atr
        )
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """
        Calculate Relative Strength Index
        
        Args:
            prices: Array of prices
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        # Calculate RS and RSI
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def _calculate_atr(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        period: int = 14
    ) -> float:
        """
        Calculate Average True Range
        
        Args:
            highs: Array of high prices
            lows: Array of low prices
            closes: Array of close prices
            period: ATR period (default 14)
            
        Returns:
            ATR value
        """
        # Calculate true range
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Calculate ATR as average of true range
        atr = float(np.mean(true_range[-period:]))
        
        return atr
    
    async def get_latest_quote(self, pair: str) -> dict:
        """Return latest quote derived from historical CSV data."""
        historical_data = self._load_pair_history(pair)

        if not historical_data:
            raise ValueError(f"No historical data available for {pair}")

        latest = historical_data[-1]

        return {
            "pair": pair,
            "timestamp": latest.timestamp,
            "price": latest.close,
            "bid": latest.close,
            "ask": latest.close,
            "spread": 0.0,
            "source": "historical_csv"
        }
    
    async def get_volatility_metrics(
        self,
        pair: str,
        period: int = 20
    ) -> dict:
        """
        Calculate volatility metrics
        
        TODO: Implement volatility analysis
        - Historical volatility
        - Volatility percentile
        - ATR-based volatility
        - Volatility regime detection
        
        Args:
            pair: Forex currency pair
            period: Lookback period
            
        Returns:
            Volatility metrics
        """
        # TODO: Implement volatility analysis
        raise NotImplementedError("Volatility analysis not yet implemented")

    def _load_pair_history(self, pair: str) -> List[OHLCV]:
        """Load historical OHLCV data for a pair from the CSV-backed service."""
        df = self._historical_service.load_historical_data()
        pair_df = self._historical_service.get_pair_history(df, pair)

        if pair_df.empty:
            raise ValueError(f"No historical data found for {pair} in CSV")

        historical_data: List[OHLCV] = []
        for date_idx, row in pair_df.iterrows():
            price = float(row['rate'])
            timestamp = date_idx.to_pydatetime() if hasattr(date_idx, "to_pydatetime") else date_idx
            candle = OHLCV(
                timestamp=timestamp,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=0.0
            )
            historical_data.append(candle)

        if not historical_data:
            raise ValueError(f"No data points found for {pair}")

        return historical_data
