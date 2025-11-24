"""
Validation utilities
"""
from typing import Optional
from datetime import datetime

from app.core.config import settings


def validate_forex_pair(pair: str) -> bool:
    """
    Validate forex pair format and support
    
    Args:
        pair: Forex currency pair (e.g., EURUSD)
        
    Returns:
        True if valid, False otherwise
    """
    if not pair:
        return False
    
    # Check if pair is in supported list
    if pair.upper() not in settings.FOREX_PAIRS:
        return False
    
    # Check format (should be 6 characters)
    if len(pair) != 6:
        return False
    
    return True


def validate_trader_profile(profile: str) -> bool:
    """
    Validate trader profile
    
    Args:
        profile: Trader profile name
        
    Returns:
        True if valid, False otherwise
    """
    valid_profiles = ["conservative", "balanced", "aggressive"]
    return profile.lower() in valid_profiles


def validate_capital(capital: float) -> bool:
    """
    Validate trading capital
    
    Args:
        capital: Trading capital amount
        
    Returns:
        True if valid, False otherwise
    """
    return capital >= settings.MIN_CAPITAL


def validate_position_size(position_size: float, capital: float) -> bool:
    """
    Validate position size against capital
    
    Args:
        position_size: Proposed position size
        capital: Available capital
        
    Returns:
        True if valid, False otherwise
    """
    # Position size should not exceed capital
    if position_size > capital:
        return False
    
    # Position size should be positive
    if position_size <= 0:
        return False
    
    return True


def validate_leverage(leverage: float, max_leverage: float) -> bool:
    """
    Validate leverage amount
    
    Args:
        leverage: Proposed leverage
        max_leverage: Maximum allowed leverage
        
    Returns:
        True if valid, False otherwise
    """
    if leverage < 1.0:
        return False
    
    if leverage > max_leverage:
        return False
    
    return True


def validate_price(price: float) -> bool:
    """
    Validate price value
    
    Args:
        price: Price value
        
    Returns:
        True if valid, False otherwise
    """
    return price > 0


def validate_timeframe(timeframe: str) -> bool:
    """
    Validate candlestick timeframe
    
    TODO: Implement timeframe validation
    - Support: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
    
    Args:
        timeframe: Timeframe string
        
    Returns:
        True if valid, False otherwise
    """
    valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
    return timeframe.lower() in valid_timeframes


def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """
    Validate date range for backtesting
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, False otherwise
    """
    # End date should be after start date
    if end_date <= start_date:
        return False
    
    # Dates should not be in the future
    if end_date > datetime.now():
        return False
    
    return True
