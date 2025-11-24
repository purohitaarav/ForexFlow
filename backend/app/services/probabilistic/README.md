# TrendSense Implementation

## Overview

TrendSense is the probabilistic reasoning MCP tool for forex trend forecasting. It uses Bayesian inference to calculate probability distributions over possible market trends.

## Architecture

### Components

1. **Feature Extraction** (`feature_extraction.py`)
   - Converts OHLCV data and indicators into numeric features
   - Extracts 21 features across 5 categories

2. **Bayesian Forecaster** (`bayesian_forecaster.py`)
   - Implements Bayesian probabilistic reasoning
   - Calculates likelihood functions for each trend
   - Applies Bayes' theorem for posterior probabilities

3. **MCP Tool Interface** (`predict_trend.py`)
   - Validates input/output schemas
   - Converts between MCP format and internal models
   - Exposes forecasting functionality

## Feature Categories

### 1. Price Features (5 features)
- `price_change_1`: 1-period price change
- `price_change_5`: 5-period average change
- `price_change_10`: 10-period average change
- `price_std`: Price standard deviation
- `price_range`: Normalized price range

### 2. Momentum Features (4 features)
- `momentum_ratio`: Ratio of positive to total days
- `momentum_strength`: Net momentum strength
- `consecutive_ups`: Consecutive up days
- `consecutive_downs`: Consecutive down days

### 3. Volatility Features (5 features)
- `volatility_short`: 5-period volatility
- `volatility_medium`: 10-period volatility
- `volatility_long`: Full-period volatility
- `avg_true_range`: Average true range
- `volatility_trend`: Volatility change direction

### 4. Technical Indicator Features (5 features)
- `rsi`: Relative Strength Index
- `rsi_normalized`: RSI normalized to [-1, 1]
- `sma_cross`: Price vs SMA-20 crossover
- `sma_trend`: SMA-20 vs SMA-50 trend
- `atr_normalized`: ATR as fraction of price

### 5. Volume Features (2 features)
- `volume_ratio`: Recent vs average volume
- `volume_trend`: Volume change direction

## Bayesian Inference Process

### 1. Prior Probabilities
```python
P(bullish) = 0.40
P(bearish) = 0.40
P(neutral) = 0.20
```

### 2. Likelihood Calculation

For each trend direction, calculate likelihood using weighted feature sum:

```python
score = Σ(weight_i × feature_i)
likelihood = sigmoid(score) = 1 / (1 + e^(-score))
```

**Feature Weights** (examples):
- Strong signals: `momentum_ratio` (2.5), `momentum_strength` (2.0)
- Moderate signals: `sma_cross` (1.5), `sma_trend` (1.2)
- Weak signals: `volume_ratio` (0.5)
- Negative signals: `volatility` (-0.5), `price_std` (-0.3)

### 3. Posterior Calculation (Bayes' Theorem)

```python
P(trend|features) = P(features|trend) × P(trend) / P(features)

# Unnormalized posteriors
posterior_up = likelihood_up × prior_up
posterior_down = likelihood_down × prior_down
posterior_neutral = likelihood_neutral × prior_neutral

# Normalize to sum to 1
total = posterior_up + posterior_down + posterior_neutral
posterior_up /= total
posterior_down /= total
posterior_neutral /= total
```

### 4. Uncertainty Quantification

Uses Shannon entropy to measure uncertainty:

```python
entropy = -Σ(p_i × log(p_i))
uncertainty = entropy / log(3)  # Normalized to [0, 1]
```

Higher uncertainty means less confident prediction.

## Output Format

```python
{
    "direction": "bullish" | "bearish" | "neutral",
    "confidence": 0.75,  # Max probability
    "probability_up": 0.65,
    "probability_down": 0.20,
    "probability_neutral": 0.15,
    "expected_move": 0.0025,  # Expected price change
    "uncertainty_score": 0.25,
    "explanation": "Bullish trend detected with 65.0% probability. Strong positive momentum (70.0% bullish days). RSI at 55.0 indicates balanced conditions."
}
```

## Usage Example

```python
from app.mcp_tools import predict_trend

# Input data
input_data = {
    "pair": "EURUSD",
    "historical_prices": [1.1000, 1.1010, 1.1005, ...],  # Min 50 prices
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

# Get forecast
result = predict_trend(input_data)

print(f"Trend: {result['direction']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Explanation: {result['reasoning']}")
```

## Key Design Decisions

### 1. Sliding Window Approach
- Uses configurable window size (default: 20 periods)
- Focuses on recent data for better responsiveness
- Balances historical context with current conditions

### 2. Volatility Weighting
- Recent volatility weighted more heavily (50%)
- Medium-term volatility (30%)
- Long-term volatility (20%)
- Adapts to changing market conditions

### 3. Feature Normalization
- All features scaled appropriately
- RSI normalized to [-1, 1] range
- Price changes as fractions
- Ensures balanced feature contributions

### 4. Modular Design
- Separate feature extraction from forecasting
- Easy to add new features
- Easy to adjust weights
- Testable components

## Performance Characteristics

- **Speed**: ~10-20ms per forecast
- **Memory**: Minimal (stateless forecaster)
- **Accuracy**: Depends on market conditions and feature quality
- **Robustness**: Handles missing data gracefully

## Future Enhancements

1. **Adaptive Weights**: Learn feature weights from historical performance
2. **Regime Detection**: Adjust priors based on market regime
3. **Multi-Timeframe**: Combine forecasts from different timeframes
4. **Confidence Calibration**: Calibrate probabilities against actual outcomes
5. **Feature Selection**: Automatically select most predictive features

## Testing

Run tests with:
```bash
pytest tests/test_trendsense.py
```

## References

- Bayesian Inference: Murphy, "Machine Learning: A Probabilistic Perspective"
- Technical Analysis: Pring, "Technical Analysis Explained"
- Entropy Calculation: Shannon, "A Mathematical Theory of Communication"
