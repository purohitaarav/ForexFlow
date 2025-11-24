"""
Feature Extraction for TrendSense

Converts MarketState (OHLCV windows + indicators) into numeric features
for probabilistic trend forecasting.
"""
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

from app.models.market import MarketState, OHLCV, MarketIndicators


class FeatureExtractor:
    """
    Extracts numeric features from market data for trend analysis
    """
    
    def __init__(self, window_size: int = 20):
        """
        Initialize feature extractor
        
        Args:
            window_size: Number of historical candles to use for features
        """
        self.window_size = window_size
    
    def extract_features(self, market_state: MarketState) -> Dict[str, float]:
        """
        Extract all features from market state
        
        Args:
            market_state: Current market state with historical data
            
        Returns:
            Dictionary of feature names to values
        """
        features = {}
        
        # Price-based features
        features.update(self._extract_price_features(market_state))
        
        # Momentum features
        features.update(self._extract_momentum_features(market_state))
        
        # Volatility features
        features.update(self._extract_volatility_features(market_state))
        
        # Technical indicator features
        features.update(self._extract_indicator_features(market_state))
        
        # Volume features
        features.update(self._extract_volume_features(market_state))
        
        return features
    
    def _extract_price_features(self, market_state: MarketState) -> Dict[str, float]:
        """Extract price-based features"""
        historical = market_state.historical_data[-self.window_size:]
        closes = np.array([candle.close for candle in historical])
        
        # Price changes
        returns = np.diff(closes) / closes[:-1]
        
        features = {
            'price_change_1': returns[-1] if len(returns) > 0 else 0.0,
            'price_change_5': np.mean(returns[-5:]) if len(returns) >= 5 else 0.0,
            'price_change_10': np.mean(returns[-10:]) if len(returns) >= 10 else 0.0,
            'price_std': np.std(closes),
            'price_range': (np.max(closes) - np.min(closes)) / np.mean(closes),
        }
        
        return features
    
    def _extract_momentum_features(self, market_state: MarketState) -> Dict[str, float]:
        """Extract momentum-based features"""
        historical = market_state.historical_data[-self.window_size:]
        closes = np.array([candle.close for candle in historical])
        
        # Calculate momentum indicators
        returns = np.diff(closes) / closes[:-1]
        
        # Count positive vs negative days
        positive_days = np.sum(returns > 0)
        negative_days = np.sum(returns < 0)
        total_days = len(returns)
        
        # Momentum strength
        positive_momentum = np.sum(returns[returns > 0]) if np.any(returns > 0) else 0.0
        negative_momentum = abs(np.sum(returns[returns < 0])) if np.any(returns < 0) else 0.0
        
        features = {
            'momentum_ratio': positive_days / total_days if total_days > 0 else 0.5,
            'momentum_strength': positive_momentum - negative_momentum,
            'consecutive_ups': self._count_consecutive(returns > 0),
            'consecutive_downs': self._count_consecutive(returns < 0),
        }
        
        return features
    
    def _extract_volatility_features(self, market_state: MarketState) -> Dict[str, float]:
        """Extract volatility-based features"""
        historical = market_state.historical_data[-self.window_size:]
        
        highs = np.array([candle.high for candle in historical])
        lows = np.array([candle.low for candle in historical])
        closes = np.array([candle.close for candle in historical])
        
        # True range
        tr = np.maximum(highs[1:] - lows[1:], 
                       np.maximum(abs(highs[1:] - closes[:-1]),
                                 abs(lows[1:] - closes[:-1])))
        
        # Returns volatility
        returns = np.diff(closes) / closes[:-1]
        
        features = {
            'volatility_short': np.std(returns[-5:]) if len(returns) >= 5 else 0.0,
            'volatility_medium': np.std(returns[-10:]) if len(returns) >= 10 else 0.0,
            'volatility_long': np.std(returns),
            'avg_true_range': np.mean(tr) if len(tr) > 0 else 0.0,
            'volatility_trend': self._calculate_volatility_trend(returns),
        }
        
        return features
    
    def _extract_indicator_features(self, market_state: MarketState) -> Dict[str, float]:
        """Extract technical indicator features"""
        indicators = market_state.indicators
        
        features = {
            'rsi': indicators.rsi,
            'rsi_normalized': (indicators.rsi - 50) / 50,  # Normalize to [-1, 1]
            'sma_cross': (market_state.current_price - indicators.sma_20) / indicators.sma_20,
            'sma_trend': (indicators.sma_20 - indicators.sma_50) / indicators.sma_50,
            'atr_normalized': indicators.atr / market_state.current_price,
        }
        
        return features
    
    def _extract_volume_features(self, market_state: MarketState) -> Dict[str, float]:
        """Extract volume-based features"""
        historical = market_state.historical_data[-self.window_size:]
        volumes = np.array([candle.volume for candle in historical])
        
        avg_volume = np.mean(volumes)
        recent_volume = np.mean(volumes[-5:]) if len(volumes) >= 5 else avg_volume
        
        features = {
            'volume_ratio': recent_volume / avg_volume if avg_volume > 0 else 1.0,
            'volume_trend': (volumes[-1] - avg_volume) / avg_volume if avg_volume > 0 else 0.0,
        }
        
        return features
    
    def _count_consecutive(self, condition: np.ndarray) -> int:
        """Count consecutive True values at the end of array"""
        if len(condition) == 0:
            return 0
        
        count = 0
        for val in reversed(condition):
            if val:
                count += 1
            else:
                break
        return count
    
    def _calculate_volatility_trend(self, returns: np.ndarray) -> float:
        """
        Calculate if volatility is increasing or decreasing
        
        Returns:
            Positive if volatility increasing, negative if decreasing
        """
        if len(returns) < 10:
            return 0.0
        
        recent_vol = np.std(returns[-5:])
        older_vol = np.std(returns[-10:-5])
        
        if older_vol == 0:
            return 0.0
        
        return (recent_vol - older_vol) / older_vol
    
    def get_feature_vector(self, market_state: MarketState) -> np.ndarray:
        """
        Get features as a numpy array
        
        Args:
            market_state: Current market state
            
        Returns:
            Feature vector as numpy array
        """
        features = self.extract_features(market_state)
        return np.array(list(features.values()))
    
    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names in order
        
        Returns:
            List of feature names
        """
        # Return in consistent order
        return [
            'price_change_1', 'price_change_5', 'price_change_10',
            'price_std', 'price_range',
            'momentum_ratio', 'momentum_strength',
            'consecutive_ups', 'consecutive_downs',
            'volatility_short', 'volatility_medium', 'volatility_long',
            'avg_true_range', 'volatility_trend',
            'rsi', 'rsi_normalized', 'sma_cross', 'sma_trend', 'atr_normalized',
            'volume_ratio', 'volume_trend'
        ]
