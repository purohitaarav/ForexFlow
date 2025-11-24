"""
Bayesian Trend Forecaster

Implements Bayesian probabilistic reasoning for trend prediction.
Uses prior probabilities and likelihood updates based on market features.
"""
import numpy as np
from typing import Dict, Tuple
from scipy.stats import norm

from app.services.probabilistic.feature_extraction import FeatureExtractor
from app.models.market import MarketState


class BayesianTrendForecaster:
    """
    Bayesian inference for trend forecasting
    
    Uses:
    - Prior probabilities based on historical trend distribution
    - Likelihood functions based on feature values
    - Posterior probability calculation via Bayes' theorem
    """
    
    def __init__(self):
        """Initialize Bayesian forecaster"""
        self.feature_extractor = FeatureExtractor()
        
        # Prior probabilities (neutral starting point)
        self.prior_up = 0.40
        self.prior_down = 0.40
        self.prior_neutral = 0.20
        
        # Feature weights (learned from domain knowledge)
        self.feature_weights = self._initialize_feature_weights()
    
    def _initialize_feature_weights(self) -> Dict[str, float]:
        """
        Initialize feature weights for likelihood calculation
        
        These weights represent how much each feature influences
        the probability of an upward trend.
        """
        return {
            # Price features (strong signals)
            'price_change_1': 2.0,
            'price_change_5': 1.5,
            'price_change_10': 1.0,
            'price_std': -0.3,  # High volatility reduces confidence
            'price_range': -0.2,
            
            # Momentum features (strong signals)
            'momentum_ratio': 2.5,
            'momentum_strength': 2.0,
            'consecutive_ups': 1.5,
            'consecutive_downs': -1.5,
            
            # Volatility features (moderate signals)
            'volatility_short': -0.5,
            'volatility_medium': -0.3,
            'volatility_long': -0.2,
            'avg_true_range': -0.3,
            'volatility_trend': -0.4,
            
            # Technical indicators (moderate signals)
            'rsi': 0.5,
            'rsi_normalized': 1.0,
            'sma_cross': 1.5,
            'sma_trend': 1.2,
            'atr_normalized': -0.3,
            
            # Volume features (weak signals)
            'volume_ratio': 0.5,
            'volume_trend': 0.3,
        }
    
    def forecast(self, market_state: MarketState) -> Dict[str, float]:
        """
        Generate probabilistic trend forecast
        
        Args:
            market_state: Current market state
            
        Returns:
            Dictionary with probabilities and metrics
        """
        # Extract features
        features = self.feature_extractor.extract_features(market_state)
        
        # Calculate likelihoods
        likelihood_up = self._calculate_likelihood_up(features)
        likelihood_down = self._calculate_likelihood_down(features)
        likelihood_neutral = self._calculate_likelihood_neutral(features)
        
        # Apply Bayes' theorem
        posterior_up, posterior_down, posterior_neutral = self._calculate_posteriors(
            likelihood_up, likelihood_down, likelihood_neutral
        )
        
        # Calculate volatility and uncertainty
        volatility = self._calculate_volatility(features)
        uncertainty = self._calculate_uncertainty(posterior_up, posterior_down, posterior_neutral)
        
        # Determine dominant trend
        trend_direction = self._determine_trend(posterior_up, posterior_down, posterior_neutral)
        
        # Calculate expected move
        expected_move = self._calculate_expected_move(
            posterior_up, posterior_down, features, market_state
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            features, posterior_up, posterior_down, posterior_neutral, trend_direction
        )
        
        return {
            'probability_up': posterior_up,
            'probability_down': posterior_down,
            'probability_neutral': posterior_neutral,
            'direction': trend_direction,
            'confidence': max(posterior_up, posterior_down, posterior_neutral),
            'volatility': volatility,
            'uncertainty_score': uncertainty,
            'expected_move': expected_move,
            'explanation': explanation
        }
    
    def _calculate_likelihood_up(self, features: Dict[str, float]) -> float:
        """
        Calculate likelihood of upward trend given features
        
        Uses weighted sum of features with sigmoid transformation
        """
        score = 0.0
        
        for feature_name, feature_value in features.items():
            weight = self.feature_weights.get(feature_name, 0.0)
            score += weight * feature_value
        
        # Apply sigmoid to convert to probability
        likelihood = 1 / (1 + np.exp(-score))
        
        return likelihood
    
    def _calculate_likelihood_down(self, features: Dict[str, float]) -> float:
        """
        Calculate likelihood of downward trend given features
        
        Inverse of upward likelihood with adjustments
        """
        # Flip signs for downward features
        flipped_features = {}
        for name, value in features.items():
            if 'down' in name.lower():
                flipped_features[name] = value
            else:
                flipped_features[name] = -value
        
        score = 0.0
        for feature_name, feature_value in flipped_features.items():
            weight = self.feature_weights.get(feature_name, 0.0)
            score += weight * feature_value
        
        likelihood = 1 / (1 + np.exp(-score))
        
        return likelihood
    
    def _calculate_likelihood_neutral(self, features: Dict[str, float]) -> float:
        """
        Calculate likelihood of neutral/sideways trend
        
        Based on low momentum and balanced indicators
        """
        # Neutral is likely when momentum is weak and volatility is low
        momentum_strength = abs(features.get('momentum_strength', 0.0))
        volatility = features.get('volatility_medium', 0.0)
        rsi_neutral = 1.0 - abs(features.get('rsi_normalized', 0.0))
        
        # Neutral score increases with weak momentum and balanced RSI
        neutral_score = (1.0 - momentum_strength) * rsi_neutral * (1.0 - volatility * 10)
        
        # Ensure in [0, 1] range
        likelihood = max(0.0, min(1.0, neutral_score))
        
        return likelihood
    
    def _calculate_posteriors(
        self,
        likelihood_up: float,
        likelihood_down: float,
        likelihood_neutral: float
    ) -> Tuple[float, float, float]:
        """
        Calculate posterior probabilities using Bayes' theorem
        
        P(trend|features) = P(features|trend) * P(trend) / P(features)
        """
        # Calculate unnormalized posteriors
        posterior_up = likelihood_up * self.prior_up
        posterior_down = likelihood_down * self.prior_down
        posterior_neutral = likelihood_neutral * self.prior_neutral
        
        # Normalize to sum to 1
        total = posterior_up + posterior_down + posterior_neutral
        
        if total > 0:
            posterior_up /= total
            posterior_down /= total
            posterior_neutral /= total
        else:
            # Fallback to priors if likelihoods are all zero
            posterior_up = self.prior_up
            posterior_down = self.prior_down
            posterior_neutral = self.prior_neutral
        
        return posterior_up, posterior_down, posterior_neutral
    
    def _calculate_volatility(self, features: Dict[str, float]) -> float:
        """Calculate overall volatility metric"""
        vol_short = features.get('volatility_short', 0.0)
        vol_medium = features.get('volatility_medium', 0.0)
        vol_long = features.get('volatility_long', 0.0)
        
        # Weighted average favoring recent volatility
        volatility = (0.5 * vol_short + 0.3 * vol_medium + 0.2 * vol_long)
        
        return volatility
    
    def _calculate_uncertainty(
        self,
        prob_up: float,
        prob_down: float,
        prob_neutral: float
    ) -> float:
        """
        Calculate uncertainty using entropy
        
        Higher entropy = higher uncertainty
        """
        probs = np.array([prob_up, prob_down, prob_neutral])
        
        # Avoid log(0)
        probs = np.clip(probs, 1e-10, 1.0)
        
        # Calculate entropy
        entropy = -np.sum(probs * np.log(probs))
        
        # Normalize to [0, 1] (max entropy for 3 outcomes is log(3))
        max_entropy = np.log(3)
        uncertainty = entropy / max_entropy
        
        return uncertainty
    
    def _determine_trend(
        self,
        prob_up: float,
        prob_down: float,
        prob_neutral: float
    ) -> str:
        """Determine dominant trend direction"""
        max_prob = max(prob_up, prob_down, prob_neutral)
        
        if max_prob == prob_up:
            return 'bullish'
        elif max_prob == prob_down:
            return 'bearish'
        else:
            return 'neutral'
    
    def _calculate_expected_move(
        self,
        prob_up: float,
        prob_down: float,
        features: Dict[str, float],
        market_state: MarketState
    ) -> float:
        """
        Calculate expected price movement
        
        Uses probability-weighted average of potential moves
        """
        # Estimate move size from volatility and momentum
        volatility = features.get('volatility_medium', 0.01)
        momentum = features.get('momentum_strength', 0.0)
        
        # Expected move in one direction (as fraction of price)
        base_move = volatility * 2.0  # Typical move is ~2x volatility
        
        # Adjust by momentum
        upward_move = base_move * (1.0 + momentum)
        downward_move = base_move * (1.0 - momentum)
        
        # Probability-weighted expected move
        expected_move = (prob_up * upward_move) - (prob_down * downward_move)
        
        # Convert to absolute price change
        expected_move_abs = abs(expected_move * market_state.current_price)
        
        return expected_move_abs
    
    def _generate_explanation(
        self,
        features: Dict[str, float],
        prob_up: float,
        prob_down: float,
        prob_neutral: float,
        trend: str
    ) -> str:
        """Generate human-readable explanation of forecast"""
        
        # Identify strongest signals
        momentum_ratio = features.get('momentum_ratio', 0.5)
        rsi = features.get('rsi', 50.0)
        sma_cross = features.get('sma_cross', 0.0)
        volatility = features.get('volatility_medium', 0.0)
        
        explanation_parts = []
        
        # Trend statement
        if trend == 'bullish':
            explanation_parts.append(f"Bullish trend detected with {prob_up:.1%} probability.")
        elif trend == 'bearish':
            explanation_parts.append(f"Bearish trend detected with {prob_down:.1%} probability.")
        else:
            explanation_parts.append(f"Neutral/sideways trend with {prob_neutral:.1%} probability.")
        
        # Momentum analysis
        if momentum_ratio > 0.6:
            explanation_parts.append(f"Strong positive momentum ({momentum_ratio:.1%} bullish days).")
        elif momentum_ratio < 0.4:
            explanation_parts.append(f"Strong negative momentum ({1-momentum_ratio:.1%} bearish days).")
        else:
            explanation_parts.append("Balanced momentum with mixed signals.")
        
        # RSI analysis
        if rsi > 70:
            explanation_parts.append(f"RSI at {rsi:.1f} indicates overbought conditions.")
        elif rsi < 30:
            explanation_parts.append(f"RSI at {rsi:.1f} indicates oversold conditions.")
        
        # SMA analysis
        if sma_cross > 0.01:
            explanation_parts.append("Price above SMA-20, indicating upward momentum.")
        elif sma_cross < -0.01:
            explanation_parts.append("Price below SMA-20, indicating downward pressure.")
        
        # Volatility note
        if volatility > 0.02:
            explanation_parts.append(f"High volatility ({volatility:.2%}) increases uncertainty.")
        
        return " ".join(explanation_parts)
