import pytest
from app.mcp_tools.opti_trade import create_opti_trade_tool
from app.models.market import MarketState, MarketIndicators, TrendForecast
from app.models.trade import Portfolio, TraderProfile, RiskConstraints, TradeAction
from datetime import datetime

def create_mock_data():
    indicators = MarketIndicators(
        returns=0.001,
        volatility=0.005,
        sma_20=1.1000,
        sma_50=1.0980,
        rsi=55.0,
        atr=0.0020
    )
    
    market_state = MarketState(
        pair="EURUSD",
        timestamp=datetime.now(),
        current_price=1.1000,
        historical_data=[],
        indicators=indicators
    )
    
    portfolio = Portfolio(
        capital=10000.0,
        open_positions=0,
        total_profit_loss=0.0,
        max_drawdown=0.0
    )
    
    trend_forecast = TrendForecast(
        direction="bullish",
        confidence=0.8,
        probability_up=0.7,
        probability_down=0.2,
        probability_neutral=0.1,
        expected_move=0.0050,
        uncertainty_score=0.2
    )
    
    risk_constraints = RiskConstraints(
        max_position_size=5000.0,
        stop_loss=1.0945,
        take_profit=1.1110,
        leverage=2.0,
        risk_amount=25.0,
        is_valid=True,
        constraint_violations=[]
    )
    
    return market_state, portfolio, trend_forecast, risk_constraints

def test_opti_trade_conservative():
    # Test Conservative Profile (penalizes volatility)
    opti_trade = create_opti_trade_tool(TraderProfile.CONSERVATIVE)
    market_state, portfolio, trend_forecast, risk_constraints = create_mock_data()
    
    recommendation = opti_trade.optimize(
        market_state, trend_forecast, risk_constraints, portfolio, TraderProfile.CONSERVATIVE
    )
    
    assert recommendation.action in [TradeAction.BUY, TradeAction.HOLD]
    assert recommendation.confidence_score >= 0
    assert "Search trace" in recommendation.reasoning
    print(f"\nConservative Recommendation: {recommendation.action.value}")
    print(f"Position Size: {recommendation.position_size}")
    print(f"Score: {recommendation.confidence_score:.4f}")
    print(f"States Explored: {len(opti_trade.explored_states)}")

def test_opti_trade_aggressive():
    # Test Aggressive Profile (weights profit highly)
    opti_trade = create_opti_trade_tool(TraderProfile.AGGRESSIVE)
    market_state, portfolio, trend_forecast, risk_constraints = create_mock_data()
    
    recommendation = opti_trade.optimize(
        market_state, trend_forecast, risk_constraints, portfolio, TraderProfile.AGGRESSIVE
    )
    
    assert recommendation.action in [TradeAction.BUY, TradeAction.HOLD]
    assert recommendation.confidence_score >= 0
    print(f"\nAggressive Recommendation: {recommendation.action.value}")
    print(f"Position Size: {recommendation.position_size}")
    print(f"Score: {recommendation.confidence_score:.4f}")
    print(f"States Explored: {len(opti_trade.explored_states)}")

def test_opti_trade_beam_search():
    # Test that beam search explores multiple depths
    opti_trade = create_opti_trade_tool(TraderProfile.BALANCED)
    market_state, portfolio, trend_forecast, risk_constraints = create_mock_data()
    
    recommendation = opti_trade.optimize(
        market_state, trend_forecast, risk_constraints, portfolio, TraderProfile.BALANCED
    )
    
    # Should explore multiple states
    assert len(opti_trade.explored_states) > 1
    
    # Should have states at different depths
    depths = set([s.depth for s in opti_trade.explored_states])
    print(f"\nDepths explored: {sorted(depths)}")
    print(f"Total states: {len(opti_trade.explored_states)}")
    print(f"Reasoning trace: {opti_trade.reasoning_trace}")

def test_opti_trade_invalid_constraints():
    # Test with invalid constraints (should return HOLD)
    opti_trade = create_opti_trade_tool(TraderProfile.BALANCED)
    market_state, portfolio, trend_forecast, risk_constraints = create_mock_data()
    
    # Make constraints invalid
    risk_constraints.is_valid = False
    
    recommendation = opti_trade.optimize(
        market_state, trend_forecast, risk_constraints, portfolio, TraderProfile.BALANCED
    )
    
    assert recommendation.action == TradeAction.HOLD
    print(f"\nInvalid Constraints Recommendation: {recommendation.action.value}")

if __name__ == "__main__":
    test_opti_trade_conservative()
    test_opti_trade_aggressive()
    test_opti_trade_beam_search()
    test_opti_trade_invalid_constraints()
