import pytest
from app.mcp_tools.risk_guard import create_risk_guard_tool
from app.models.market import MarketState, MarketIndicators, TrendForecast
from app.models.trade import Portfolio, TraderProfile
from app.core.config import settings

def create_mock_data():
    indicators = MarketIndicators(
        returns=0.001,
        volatility=0.005,
        sma_20=1.1000,
        sma_50=1.0980,
        rsi=55.0,
        atr=0.0020
    )
    
    from datetime import datetime
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
    
    return market_state, portfolio, trend_forecast

def test_risk_guard_conservative():
    # Test Conservative Profile (0.5% risk)
    risk_guard = create_risk_guard_tool()
    market_state, portfolio, trend_forecast = create_mock_data()
    
    constraints = risk_guard.validate_and_optimize(
        market_state, trend_forecast, portfolio, TraderProfile.CONSERVATIVE
    )
    
    assert constraints.is_valid
    assert constraints.risk_amount <= portfolio.capital * 0.005
    assert constraints.leverage <= 2.0
    print(f"\nConservative Constraints: {constraints}")

def test_risk_guard_aggressive():
    # Test Aggressive Profile (3.0% risk)
    risk_guard = create_risk_guard_tool()
    market_state, portfolio, trend_forecast = create_mock_data()
    
    constraints = risk_guard.validate_and_optimize(
        market_state, trend_forecast, portfolio, TraderProfile.AGGRESSIVE
    )
    
    assert constraints.is_valid
    # Should allow more risk than conservative
    # Note: The solver tries to maximize, so it should be close to limit
    assert constraints.risk_amount <= portfolio.capital * 0.03
    assert constraints.leverage <= 10.0
    print(f"\nAggressive Constraints: {constraints}")

def test_risk_guard_no_solution():
    # Test case where no solution is possible (e.g. very low capital or high volatility requiring wide stops)
    risk_guard = create_risk_guard_tool()
    market_state, portfolio, trend_forecast = create_mock_data()
    
    # Set capital very low so min position size (100) violates risk limits
    portfolio.capital = 10.0 
    
    constraints = risk_guard.validate_and_optimize(
        market_state, trend_forecast, portfolio, TraderProfile.CONSERVATIVE
    )
    
    assert not constraints.is_valid
    print(f"\nNo Solution Constraints: {constraints}")

if __name__ == "__main__":
    test_risk_guard_conservative()
    test_risk_guard_aggressive()
    test_risk_guard_no_solution()
