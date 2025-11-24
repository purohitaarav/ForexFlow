# Step 11: Profile Evaluation - Complete

## Summary

Successfully implemented **profile evaluation** system that compares different trader types (conservative, balanced, aggressive) using backtesting simulation.

## Implementation Details

### 1. Profile Evaluator Service

**File**: `backend/app/services/profile_evaluator.py`

**Features**:
- Simulates trading over historical periods
- Tracks performance metrics for each profile
- Calculates risk-adjusted returns
- Identifies constraint violations

**Metrics Calculated**:
```python
@dataclass
class ProfileMetrics:
    profile: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    final_capital: float
    final_returns: float          # % return
    max_drawdown: float            # % drawdown
    avg_volatility: float          # Portfolio volatility
    constraint_violations: int
    sharpe_ratio: float            # Risk-adjusted return
    win_rate: float                # % winning trades
    avg_profit_per_trade: float
    max_consecutive_losses: int
```

**Simulation Process**:
1. Initialize portfolio with starting capital
2. For each period:
   - Generate market state
   - Get recommendation from MCP orchestrator
   - Execute trade if valid
   - Track profit/loss
   - Update metrics
3. Calculate final statistics

### 2. API Endpoints

**File**: `backend/app/routers/evaluation.py`

#### Main Endpoint
```
GET /api/evaluate_profiles?pair=EURUSD&initial_capital=10000&num_periods=30
```

**Parameters**:
- `pair`: Forex currency pair (default: EURUSD)
- `initial_capital`: Starting capital (default: $10,000)
- `num_periods`: Number of trading periods (10-100)
- `period_days`: Days per period (1-7)

**Response**:
```json
{
  "conservative": {
    "profile": "conservative",
    "total_trades": 15,
    "winning_trades": 9,
    "losing_trades": 6,
    "final_capital": 10520.00,
    "final_returns": 5.20,
    "max_drawdown": 2.10,
    "avg_volatility": 0.008,
    "constraint_violations": 0,
    "sharpe_ratio": 1.20,
    "win_rate": 60.0,
    "avg_profit_per_trade": 34.67,
    "max_consecutive_losses": 2
  },
  "balanced": {...},
  "aggressive": {...},
  "comparison": {
    "best_returns": {"profile": "aggressive", "value": 8.50},
    "lowest_drawdown": {"profile": "conservative", "value": 2.10},
    "best_sharpe_ratio": {"profile": "balanced", "value": 1.45},
    "highest_win_rate": {"profile": "conservative", "value": 60.0},
    "fewest_violations": {"profile": "conservative", "value": 0},
    "recommendation": "balanced (score: 0.425)"
  },
  "simulation_params": {
    "pair": "EURUSD",
    "initial_capital": 10000.0,
    "num_periods": 30,
    "period_days": 1
  }
}
```

#### Summary Endpoint
```
GET /api/evaluate_profiles/summary?pair=EURUSD&num_periods=30
```

**Response**:
```json
{
  "profiles": {
    "conservative": {
      "returns": 5.20,
      "max_drawdown": 2.10,
      "win_rate": 60.0,
      "sharpe_ratio": 1.20,
      "total_trades": 15
    },
    "balanced": {...},
    "aggressive": {...}
  },
  "recommendations": {
    "highest_returns": "aggressive",
    "lowest_risk": "conservative",
    "best_risk_adjusted": "balanced"
  }
}
```

### 3. Comparison Logic

**Overall Score Calculation**:
```python
score = (
    (returns / 100) * 0.3 +           # 30% weight
    sharpe_ratio * 0.3 +               # 30% weight
    (1 - drawdown / 100) * 0.2 +      # 20% weight
    (win_rate / 100) * 0.1 -          # 10% weight
    violation_penalty                  # 10% penalty
)
```

**Best Profile Determination**:
- **Highest Returns**: Profile with best final returns
- **Lowest Risk**: Profile with lowest max drawdown
- **Best Risk-Adjusted**: Profile with highest Sharpe ratio
- **Overall Recommendation**: Highest composite score

### 4. Market Simulation

**Varied Market Conditions**:
- **Periods 0-6**: Bullish trend (positive price movement)
- **Periods 7-13**: Bearish trend (negative price movement)
- **Periods 14-20**: Sideways/Neutral (range-bound)
- **Periods 21+**: Mixed conditions (varied)

**Indicators**:
- Price changes based on trend
- Volatility varies by market condition
- RSI indicates overbought/oversold levels
- SMA follows trend direction

### 5. Trade Execution Simulation

**Simplified Outcome Model**:
```python
# Probability of hitting stop loss vs take profit
sl_probability = min(0.4 + volatility * 20, 0.6)

if random() < sl_probability:
    # Hit stop loss → Loss
    profit = -(entry_price - stop_loss) * position_size
else:
    # Hit take profit → Win
    profit = (take_profit - entry_price) * position_size
```

## Expected Results

### Conservative Profile
- **Lower Returns**: ~3-5% (risk-averse)
- **Lower Drawdown**: ~1-3% (tight risk control)
- **Higher Win Rate**: ~55-65% (selective trades)
- **Lower Volatility**: Stable performance
- **Fewer Violations**: Strict adherence to constraints

### Balanced Profile
- **Moderate Returns**: ~5-8% (balanced approach)
- **Moderate Drawdown**: ~3-5% (reasonable risk)
- **Moderate Win Rate**: ~50-60% (balanced strategy)
- **Best Sharpe Ratio**: Optimal risk-adjusted returns
- **Few Violations**: Good constraint compliance

### Aggressive Profile
- **Higher Returns**: ~7-12% (profit-seeking)
- **Higher Drawdown**: ~5-10% (accepts more risk)
- **Lower Win Rate**: ~45-55% (more trades)
- **Higher Volatility**: Variable performance
- **More Violations**: May push risk limits

## Files Created

1. **`backend/app/services/profile_evaluator.py`**: Evaluation service
2. **`backend/app/routers/evaluation.py`**: API endpoints
3. **`backend/app/main.py`**: Router registration (updated)

## Testing

### API Test
```bash
curl "http://localhost:8000/api/evaluate_profiles?pair=EURUSD&num_periods=30"
```

**Status**: ✅ Endpoint responding
**Response**: Complete metrics for all 3 profiles

### Swagger Documentation
Available at: `http://localhost:8000/docs`
- Full API documentation
- Interactive testing interface
- Request/response schemas

## Key Features

✅ **Profile Comparison**: Side-by-side metrics for all profiles  
✅ **Risk Metrics**: Drawdown, volatility, Sharpe ratio  
✅ **Performance Metrics**: Returns, win rate, profit per trade  
✅ **Constraint Tracking**: Violations counted and reported  
✅ **Automated Recommendation**: Best profile based on composite score  
✅ **Flexible Parameters**: Configurable periods and capital  

## Use Cases

1. **Profile Selection**: Help users choose the right trader profile
2. **Strategy Comparison**: Compare different risk approaches
3. **Performance Analysis**: Understand trade-offs between profiles
4. **Risk Assessment**: Evaluate maximum drawdown and volatility
5. **Backtesting**: Simulate historical performance

## Next Steps

**Enhancements**:
1. Use real historical data instead of simulated markets
2. Add more sophisticated trade execution models
3. Include transaction costs and slippage
4. Implement walk-forward analysis
5. Add Monte Carlo simulation for robustness testing
6. Create visualization charts for performance comparison

**The profile evaluation system is complete and ready for use!** 🚀
