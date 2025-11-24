# Step 8: OptiTrade Implementation - Complete

## Summary

Successfully implemented **OptiTrade** as a classical AI search module using **Beam Search** with trader-profile-specific heuristics.

## Implementation Details

### 1. Search Algorithm: Beam Search
- **Multi-depth exploration**: Explores up to `max_depth` levels (default: 3)
- **Beam width**: Maintains top-k candidates at each level (default: 5)
- **State space**: Portfolio + market state + trade parameters
- **Actions**:
  - `open_trade` (BUY/SELL with varying position sizes)
  - `close_trade` (close existing positions)
  - `adjust_size` (modify position size ±25%)
  - `HOLD` (no action)

### 2. Trader-Profile-Specific Heuristics

#### Conservative Profile
- **Weights**: 25% profit, 35% risk-reward, 15% trend alignment, 10% confidence
- **Penalties**: -10% volatility, -5% drawdown
- **Behavior**: Penalizes high volatility and drawdown heavily

#### Balanced Profile
- **Weights**: 35% profit, 30% risk-reward, 20% trend alignment, 10% confidence
- **Penalties**: -5% volatility
- **Behavior**: Balanced approach between profit and risk

#### Aggressive Profile
- **Weights**: 60% profit, 20% risk-reward, 15% trend alignment, 5% confidence
- **Penalties**: None
- **Behavior**: Maximizes expected profit, ignores volatility

### 3. Reasoning Trace
Each recommendation includes:
- State-level reasoning (e.g., "Open BUY position (100% of max size)")
- Search statistics (states explored, depths reached, execution time)
- Full search trace showing beam evolution

## Test Results

```
Conservative Recommendation: buy
Position Size: 4882.8125
Score: 0.4214
States Explored: 27

Aggressive Recommendation: buy
Position Size: 4882.8125
Score: 0.2977
States Explored: 27

Depths explored: [0, 1, 2, 3]
Total states: 27
Reasoning trace: 
  - Generated 4 initial candidate states
  - Depth 0: Evaluated 4 states, kept top 4
  - Depth 1: Evaluated 5 states, kept top 5
  - Depth 2: Evaluated 9 states, kept top 5
  - Depth 3: Evaluated 9 states, kept top 5
  - Search completed in 0.14ms
  - Best state score: 0.4288

Invalid Constraints Recommendation: hold
```

## Files Modified

1. **`backend/app/mcp_tools/opti_trade.py`**: Implemented full Beam Search with trader-profile-specific heuristics
2. **`backend/app/mcp_tools/find_best_trade.py`**: Connected MCP wrapper to OptiTradeTool
3. **`backend/app/models/trade.py`**: Updated TradeRecommendation to allow zero values for HOLD actions
4. **`backend/tests/test_opti_trade.py`**: Created comprehensive tests

## Key Features

✅ **Beam Search**: Multi-depth exploration with configurable beam width  
✅ **Trader Profiles**: Conservative, Balanced, Aggressive with different heuristics  
✅ **State Actions**: open_trade, close_trade, adjust_size, HOLD  
✅ **Reasoning Trace**: Full explainability of search process  
✅ **Performance**: Fast execution (~0.14ms for 27 states)  

## Next Steps

Step 9: Build MCP orchestrator pipeline to coordinate TrendSense → OptiTrade → RiskGuard
