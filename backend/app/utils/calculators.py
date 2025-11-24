"""
Financial calculation utilities
"""
import numpy as np
from typing import List


def calculate_profit_loss(
    entry_price: float,
    exit_price: float,
    position_size: float,
    action: str
) -> float:
    """
    Calculate profit/loss for a trade
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        position_size: Position size
        action: Trade action (buy/sell)
        
    Returns:
        Profit/loss amount
    """
    if action.lower() == "buy":
        pnl = (exit_price - entry_price) * position_size
    else:  # sell
        pnl = (entry_price - exit_price) * position_size
    
    return pnl


def calculate_pip_value(
    pair: str,
    position_size: float,
    account_currency: str = "USD"
) -> float:
    """
    Calculate pip value for a forex pair
    
    TODO: Implement pip value calculation
    - Handle different pair types (XXX/USD, USD/XXX, XXX/XXX)
    - Account for position size
    - Convert to account currency
    
    Args:
        pair: Forex pair
        position_size: Position size
        account_currency: Account currency
        
    Returns:
        Pip value in account currency
    """
    # TODO: Implement proper pip value calculation
    # Simplified for now
    return position_size * 0.0001


def calculate_risk_reward_ratio(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    action: str
) -> float:
    """
    Calculate risk-reward ratio
    
    Args:
        entry_price: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        action: Trade action (buy/sell)
        
    Returns:
        Risk-reward ratio
    """
    if action.lower() == "buy":
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
    else:  # sell
        risk = abs(stop_loss - entry_price)
        reward = abs(entry_price - take_profit)
    
    if risk == 0:
        return 0.0
    
    return reward / risk


def calculate_position_size_by_risk(
    capital: float,
    risk_percentage: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calculate position size based on risk percentage
    
    Args:
        capital: Available capital
        risk_percentage: Risk as percentage of capital (e.g., 0.02 for 2%)
        entry_price: Entry price
        stop_loss: Stop loss price
        
    Returns:
        Recommended position size
    """
    risk_amount = capital * risk_percentage
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk == 0:
        return 0.0
    
    position_size = risk_amount / price_risk
    
    return position_size


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0
    
    returns_array = np.array(returns)
    
    # Calculate excess returns
    excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
    
    # Calculate Sharpe ratio
    if np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns)
    
    # Annualize
    sharpe_annual = sharpe * np.sqrt(252)
    
    return float(sharpe_annual)


def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        equity_curve: List of equity values over time
        
    Returns:
        Maximum drawdown as percentage
    """
    if len(equity_curve) == 0:
        return 0.0
    
    equity_array = np.array(equity_curve)
    
    # Calculate running maximum
    running_max = np.maximum.accumulate(equity_array)
    
    # Calculate drawdown at each point
    drawdown = (equity_array - running_max) / running_max
    
    # Return maximum drawdown (most negative value)
    max_dd = float(np.min(drawdown))
    
    return abs(max_dd)


def calculate_win_rate(trades: List[dict]) -> float:
    """
    Calculate win rate from trade history
    
    Args:
        trades: List of trade dictionaries with 'pnl' key
        
    Returns:
        Win rate as percentage (0.0 - 1.0)
    """
    if len(trades) == 0:
        return 0.0
    
    winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
    
    return winning_trades / len(trades)


def calculate_profit_factor(trades: List[dict]) -> float:
    """
    Calculate profit factor
    
    Args:
        trades: List of trade dictionaries with 'pnl' key
        
    Returns:
        Profit factor (gross profit / gross loss)
    """
    if len(trades) == 0:
        return 0.0
    
    gross_profit = sum(trade.get('pnl', 0) for trade in trades if trade.get('pnl', 0) > 0)
    gross_loss = abs(sum(trade.get('pnl', 0) for trade in trades if trade.get('pnl', 0) < 0))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def calculate_expectancy(trades: List[dict]) -> float:
    """
    Calculate expectancy (average profit per trade)
    
    Args:
        trades: List of trade dictionaries with 'pnl' key
        
    Returns:
        Average expectancy per trade
    """
    if len(trades) == 0:
        return 0.0
    
    total_pnl = sum(trade.get('pnl', 0) for trade in trades)
    
    return total_pnl / len(trades)
