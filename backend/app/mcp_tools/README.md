# MCP Tools - JSON Schema Definitions

This directory contains the MCP (Model Context Protocol) tools for ForexFlow.

## Tools

### 1. predict_trend (TrendSense)
**Type**: Probabilistic Reasoning  
**Status**: Placeholder (Algorithm NOT implemented)

**Purpose**: Forecast market trends using probabilistic models

**Input Schema** (`PredictTrendInput`):
- `pair`: Forex currency pair
- `historical_prices`: List of historical close prices (min 50)
- `indicators`: Technical indicators (returns, volatility, SMAs, RSI, ATR)
- `current_price`: Current market price
- `timestamp`: Current timestamp

**Output Schema** (`PredictTrendOutput`):
- `direction`: Predicted trend (bullish/bearish/neutral)
- `confidence`: Overall confidence score (0.0-1.0)
- `probability_up`: Probability of upward movement
- `probability_down`: Probability of downward movement
- `probability_neutral`: Probability of neutral movement
- `expected_move`: Expected price movement
- `uncertainty_score`: Uncertainty in prediction
- `reasoning`: Human-readable explanation

**Algorithm (TODO)**:
1. Extract features from historical prices
2. Calculate trend signals from indicators
3. Apply Bayesian inference for probability distribution
4. Compute uncertainty using entropy
5. Determine dominant direction
6. Generate reasoning explanation

---

### 2. check_constraints (RiskGuard)
**Type**: Constraint Satisfaction Problem (CSP)  
**Status**: Placeholder (Algorithm NOT implemented)

**Purpose**: Validate and optimize risk parameters using CSP

**Input Schema** (`CheckConstraintsInput`):
- `pair`: Forex currency pair
- `current_price`: Current market price
- `trend_forecast`: Output from predict_trend
- `portfolio`: Portfolio state (capital, positions, P&L, drawdown)
- `trader_profile`: Risk profile (conservative/balanced/aggressive)

**Output Schema** (`CheckConstraintsOutput`):
- `is_valid`: Whether constraints are satisfied
- `max_position_size`: Maximum allowed position size
- `stop_loss`: Recommended stop loss price
- `take_profit`: Recommended take profit price
- `leverage`: Recommended leverage
- `risk_amount`: Amount at risk
- `risk_percentage`: Risk as percentage of capital
- `constraint_violations`: List of violations (if any)
- `csp_variables`: CSP variables and domains
- `reasoning`: Explanation of decisions

**Algorithm (TODO)**:
1. Define CSP variables (position_size, stop_loss, take_profit, leverage)
2. Set variable domains based on trader profile
3. Define constraints (max risk, max leverage, R:R ratio, capital preservation)
4. Apply constraint propagation
5. Use backtracking search to find valid assignment
6. Optimize for best risk-reward within constraints

---

### 3. find_best_trade (OptiTrade)
**Type**: Search-Based Optimization  
**Status**: Placeholder (Algorithm NOT implemented)

**Purpose**: Find optimal trade strategy using search algorithms

**Input Schema** (`FindBestTradeInput`):
- `pair`: Forex currency pair
- `current_price`: Current market price
- `trend_forecast`: Output from predict_trend
- `risk_constraints`: Output from check_constraints
- `portfolio`: Portfolio state
- `search_config`: Search algorithm configuration (beam_width, max_depth)

**Output Schema** (`FindBestTradeOutput`):
- `action`: Recommended trade action (buy/sell/hold/close)
- `entry_price`: Entry price for the trade
- `position_size`: Recommended position size
- `stop_loss`: Stop loss price
- `take_profit`: Take profit price
- `leverage`: Leverage to use
- `expected_profit`: Expected profit
- `risk_reward_ratio`: Risk to reward ratio
- `confidence_score`: Confidence in recommendation
- `reasoning`: Explanation of recommendation
- `search_stats`: Search algorithm statistics
- `explored_states`: States explored during search

**Algorithm (TODO)**:
1. Generate initial search states (BUY/SELL/HOLD actions)
2. Define state evaluation heuristic (expected profit, R:R, trend alignment)
3. Apply beam search (maintain top-k states, expand, prune)
4. Select best state from final beam
5. Extract trade parameters from best state
6. Generate reasoning explanation

---

## Usage

### Individual Tool Usage

```python
from app.mcp_tools import predict_trend, check_constraints, find_best_trade

# Step 1: Predict trend
trend_input = {
    "pair": "EURUSD",
    "historical_prices": [...],
    "indicators": {...},
    "current_price": 1.1020,
    "timestamp": "2024-01-01T00:00:00Z"
}
trend_output = predict_trend(trend_input)

# Step 2: Check constraints
constraints_input = {
    "pair": "EURUSD",
    "current_price": 1.1020,
    "trend_forecast": trend_output,
    "portfolio": {...},
    "trader_profile": "balanced"
}
constraints_output = check_constraints(constraints_input)

# Step 3: Find best trade
trade_input = {
    "pair": "EURUSD",
    "current_price": 1.1020,
    "trend_forecast": trend_output,
    "risk_constraints": constraints_output,
    "portfolio": {...},
    "search_config": {"beam_width": 5, "max_depth": 3}
}
trade_output = find_best_trade(trade_input)
```

### Get Tool Schemas

```python
from app.mcp_tools import get_all_tool_schemas

schemas = get_all_tool_schemas()
print(schemas["predict_trend"])
print(schemas["check_constraints"])
print(schemas["find_best_trade"])
```

### Get Tool Metadata

```python
from app.mcp_tools import get_all_tool_metadata

metadata = get_all_tool_metadata()
for tool_name, meta in metadata.items():
    print(f"{tool_name}: {meta['description']}")
    print(f"  Status: {meta['status']}")
    print(f"  Type: {meta['type']}")
```

## Files

- `schemas.py` - Pydantic schemas for all tools
- `predict_trend.py` - TrendSense tool implementation
- `check_constraints.py` - RiskGuard tool implementation
- `find_best_trade.py` - OptiTrade tool implementation
- `__init__.py` - Package exports and tool registry

## Next Steps

1. Implement probabilistic reasoning algorithm in `predict_trend.py`
2. Implement CSP solver in `check_constraints.py`
3. Implement beam search in `find_best_trade.py`
4. Add unit tests for each tool
5. Add integration tests for full pipeline
6. Optimize for performance
7. Add caching layer
