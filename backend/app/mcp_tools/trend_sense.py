"""
TrendSense MCP Tool - Probabilistic Reasoning for Trend Forecasting

This tool uses probabilistic reasoning to analyze market data and produce
trend forecasts with uncertainty quantification.

Classical AI Concepts:
- Bayesian inference
- Probabilistic graphical models
- Uncertainty quantification
"""
import numpy as np
import logging
from typing import Dict, Any, Optional
from datetime import date
from app.models.market import MarketState, TrendForecast, TrendDirection
from app.services.market_state_service import get_market_state_service

logger = logging.getLogger(__name__)


class TrendSenseTool:
    """
    MCP Tool for probabilistic trend forecasting
    
    Uses historical indicators to compute probability distributions
    over possible trend directions (bullish, bearish, neutral).
    """
    
    def __init__(self):
        self.name = "trend_sense"
        self.description = "Probabilistic reasoning tool for Forex trend forecasting"
        self.market_state_service = get_market_state_service()
        
    def analyze(self, market_state: MarketState) -> TrendForecast:
        """
        Analyze market state and produce probabilistic trend forecast
        
        Args:
            market_state: Current market state with indicators
            
        Returns:
            TrendForecast with probability distributions and confidence
        """
        # TODO: Implement full probabilistic reasoning logic
        # Current implementation is a stub
        
        # Extract features for probabilistic model
        # Use the indicators computed in MarketState
        volatility = market_state.volatility_20d if market_state.volatility_20d is not None else 0.01
        sma_short = market_state.sma_short
        sma_long = market_state.sma_long
        current_price = market_state.prices[-1] if market_state.prices else 0.0
        
        # TODO: Implement Bayesian inference
        # For now, use simple heuristics as placeholder
        
        # Calculate trend signals
        trend_signal = self._calculate_trend_signal(
            current_price, sma_short, sma_long
        )
        
        # Calculate probabilities using probabilistic model
        probabilities = self._calculate_probabilities(
            trend_signal, volatility
        )
        
        # Determine dominant direction
        direction = self._determine_direction(probabilities)
        
        # Calculate confidence and uncertainty
        confidence = self._calculate_confidence(probabilities, volatility)
        uncertainty = 1.0 - confidence
        
        # Calculate expected price movement
        expected_move = self._calculate_expected_move(
            probabilities, volatility, current_price
        )
        
        return TrendForecast(
            direction=direction,
            confidence=confidence,
            probability_up=probabilities["up"],
            probability_down=probabilities["down"],
            probability_neutral=probabilities["neutral"],
            expected_move=expected_move,
            uncertainty_score=uncertainty
        )

    def predict_trend(self, pair: str, as_of_date: date, window_size: int = 60) -> Dict[str, Any]:
        """
        Main entrypoint for trend prediction using historical data.
        
        Args:
            pair: Currency pair symbol.
            as_of_date: Date for prediction.
            window_size: Historical window size.
            
        Returns:
            Dictionary with trend probabilities and explanation.
        """
        # Fetch market state using the service
        market_state = self.market_state_service.get_market_state(pair, as_of_date, window_size)
        
        # Analyze using the internal logic
        forecast = self.analyze(market_state)
        
        # Construct explanation
        explanation = (
            f"TrendSense Analysis for {pair} on {as_of_date}:\n"
            f"Direction: {forecast.direction.value.upper()} (Confidence: {forecast.confidence:.1%})\n"
            f"Probabilities: Up {forecast.probability_up:.1%}, Down {forecast.probability_down:.1%}, Neutral {forecast.probability_neutral:.1%}\n"
            f"Volatility (20d): {market_state.volatility_20d:.4f}\n"
            f"SMA Short ({market_state.sma_short:.4f}) vs SMA Long ({market_state.sma_long:.4f})"
        )
        
        return {
            "pair": pair,
            "as_of_date": as_of_date.isoformat(),
            "trend_up_prob": forecast.probability_up,
            "trend_down_prob": forecast.probability_down,
            "volatility": market_state.volatility_20d if market_state.volatility_20d else 0.0,
            "explanation": explanation
        }
    
    def _calculate_trend_signal(
        self, 
        price: float, 
        sma_short: Optional[float], 
        sma_long: Optional[float]
    ) -> float:
        """
        Calculate trend signal from moving averages.
        
        Returns value between -1 (bearish) and +1 (bullish).
        """
        # TODO: Implement sophisticated probabilistic model
        # Placeholder logic:
        
        if sma_short is None or sma_long is None or sma_long == 0:
            return 0.0
            
        # Moving average crossover signal
        # Positive if short > long (Golden Cross logic)
        ma_signal = (sma_short - sma_long) / sma_long
        
        # Price vs MA signal
        # Positive if price > long MA
        price_signal = (price - sma_long) / sma_long
        
        # Combine signals
        # Scale factors are heuristic to map typical pct diffs to [-1, 1] range
        # e.g. 1% diff -> 0.01 * 50 = 0.5 signal strength
        signal = (ma_signal * 50) + (price_signal * 50)
        
        # Clip to [-1, 1]
        return np.clip(signal, -1.0, 1.0)
    
    def _calculate_probabilities(
        self, 
        trend_signal: float, 
        volatility: float
    ) -> Dict[str, float]:
        """
        Calculate probability distribution over trend directions.
        
        Uses a heuristic Bayesian-style update:
        - Prior is uniform (0.33, 0.33, 0.33)
        - Likelihood derived from trend signal strength
        - Volatility flattens the distribution (increases uncertainty)
        """
        # TODO: Implement Bayesian inference or probabilistic graphical model
        # Placeholder using softmax-like transformation
        
        # Base logits from trend signal
        # Signal > 0 increases Up, decreases Down
        # Signal < 0 increases Down, decreases Up
        # Neutral is favored when signal is weak
        
        # Heuristic mapping:
        # Signal = 1.0 -> Strong Bull -> High Up prob
        # Signal = 0.0 -> Neutral -> High Neutral prob
        
        # Logits: [Up, Down, Neutral]
        logits = np.array([
            2.0 * trend_signal,       # Up
            -2.0 * trend_signal,      # Down
            1.0 * (1.0 - abs(trend_signal)) # Neutral
        ])
        
        # Volatility adjustment
        # Higher volatility reduces confidence in the signal -> flattens logits
        # Volatility factor: 1.0 (low vol) -> 0.5 (high vol)
        # Assume typical daily vol is ~0.005 to 0.01. High vol > 0.015
        vol_factor = 1.0 / (1.0 + volatility * 50)
        logits = logits * vol_factor
        
        # Softmax to get probabilities
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        
        return {
            "up": float(probs[0]),
            "down": float(probs[1]),
            "neutral": float(probs[2])
        }
    
    def _determine_direction(self, probabilities: Dict[str, float]) -> TrendDirection:
        """Determine dominant trend direction from probabilities"""
        max_prob = max(probabilities.values())
        
        if probabilities["up"] == max_prob:
            return TrendDirection.BULLISH
        elif probabilities["down"] == max_prob:
            return TrendDirection.BEARISH
        else:
            return TrendDirection.NEUTRAL
    
    def _calculate_confidence(
        self, 
        probabilities: Dict[str, float], 
        volatility: float
    ) -> float:
        """
        Calculate confidence score based on probability distribution
        and market volatility.
        """
        # Confidence is highest when one probability dominates
        max_prob = max(probabilities.values())
        
        # Entropy-based confidence (lower entropy = higher confidence)
        probs = np.array(list(probabilities.values()))
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        max_entropy = np.log(3)  # Maximum entropy for 3 outcomes
        
        entropy_confidence = 1.0 - (entropy / max_entropy)
        
        # Volatility penalty (high volatility reduces confidence)
        volatility_confidence = 1.0 / (1.0 + volatility * 20)
        
        # Combined confidence
        confidence = 0.7 * entropy_confidence + 0.3 * volatility_confidence
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _calculate_expected_move(
        self, 
        probabilities: Dict[str, float], 
        volatility: float,
        current_price: float
    ) -> float:
        """
        Calculate expected price movement.
        """
        # Expected move as percentage, scaled by volatility
        # If Up prob is high, expected move is positive
        net_direction = probabilities["up"] - probabilities["down"]
        
        # Magnitude depends on volatility (typical daily range)
        expected_pct = net_direction * volatility
        
        return float(expected_pct * current_price)


# MCP Tool Interface
def create_trend_sense_tool() -> TrendSenseTool:
    """Factory function to create TrendSense tool instance"""
