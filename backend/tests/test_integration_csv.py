import pytest
import asyncio
from app.core.orchestrator import orchestrator
from app.models.trade import Portfolio, TraderProfile
from app.services.market_service import MarketService

@pytest.mark.asyncio
async def test_full_recommendation_flow():
    """
    Test the full recommendation flow using CSV data.
    This verifies that:
    1. MarketService loads data from CSV.
    2. Orchestrator receives MarketState.
    3. TrendSense analyzes it.
    4. RiskGuard validates it.
    5. OptiTrade generates a recommendation.
    """
    # Setup
    pair = "EURUSD"
    portfolio = Portfolio(
        capital=10000.0,
        open_positions=0,
        total_profit_loss=0.0,
        max_drawdown=0.0
    )
    trader_profile = TraderProfile.BALANCED
    
    # 1. Get Market State (from CSV)
    market_service = MarketService()
    try:
        market_state = await market_service.get_market_state(pair)
    except ValueError as e:
        pytest.fail(f"Failed to load market state from CSV: {e}")
        
    assert market_state.pair == pair
    assert len(market_state.historical_data) > 0
    assert market_state.current_price > 0
    
    print(f"\nMarket State Loaded: {pair} at {market_state.current_price}")
    print(f"Indicators: RSI={market_state.indicators.rsi}, Volatility={market_state.indicators.volatility}")

    # 2. Get Recommendation
    recommendation = await orchestrator.recommend_trade(
        market_state=market_state,
        portfolio=portfolio,
        trader_profile=trader_profile
    )
    
    # Verification
    assert recommendation is not None
    assert "trend" in recommendation
    assert "strategy" in recommendation
    assert "risk_analysis" in recommendation
    assert "final_recommendation" in recommendation
    
    rec = recommendation["final_recommendation"]
    print(f"\nFinal Recommendation: {rec['action']} {rec['pair']}")
    print(f"Reasoning: {recommendation['explanation']}")
    
    strategy = recommendation["strategy"]
    if rec['action'] != 'hold':
        assert strategy['entry_price'] > 0
        assert strategy['stop_loss'] > 0
        assert strategy['take_profit'] > 0
        
    print("\nTest Passed Successfully!")

if __name__ == "__main__":
    # Allow running directly with python
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_full_recommendation_flow())
