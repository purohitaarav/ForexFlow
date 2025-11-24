"""
Data formatting utilities
"""
from datetime import datetime
from typing import Any, Dict


def format_price(price: float, decimals: int = 5) -> str:
    """
    Format price with appropriate decimal places
    
    Args:
        price: Price value
        decimals: Number of decimal places
        
    Returns:
        Formatted price string
    """
    return f"{price:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value (0.0 - 1.0)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount value
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    return f"{currency} {amount:,.2f}"


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def format_trade_action(action: str) -> str:
    """
    Format trade action for display
    
    Args:
        action: Trade action (buy/sell/hold)
        
    Returns:
        Formatted action string
    """
    action_map = {
        "buy": "BUY",
        "sell": "SELL",
        "hold": "HOLD",
        "close": "CLOSE"
    }
    return action_map.get(action.lower(), action.upper())


def format_trend_direction(direction: str) -> str:
    """
    Format trend direction for display
    
    Args:
        direction: Trend direction (bullish/bearish/neutral)
        
    Returns:
        Formatted direction with emoji
    """
    direction_map = {
        "bullish": "📈 Bullish",
        "bearish": "📉 Bearish",
        "neutral": "➡️ Neutral"
    }
    return direction_map.get(direction.lower(), direction.capitalize())


def format_recommendation_summary(recommendation: Dict[str, Any]) -> str:
    """
    Format trade recommendation as human-readable summary
    
    Args:
        recommendation: Trade recommendation dictionary
        
    Returns:
        Formatted summary string
    """
    action = recommendation.get('action', 'HOLD')
    pair = recommendation.get('pair', 'UNKNOWN')
    entry = recommendation.get('entry_price', 0)
    sl = recommendation.get('stop_loss', 0)
    tp = recommendation.get('take_profit', 0)
    confidence = recommendation.get('confidence_score', 0)
    
    summary = f"{format_trade_action(action)} {pair} @ {format_price(entry)}\n"
    summary += f"SL: {format_price(sl)} | TP: {format_price(tp)}\n"
    summary += f"Confidence: {format_percentage(confidence)}"
    
    return summary
