"""
Profile Evaluation Service

Evaluates different trader profiles (conservative, balanced, aggressive)
over a historical period to compare performance metrics.
"""
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.models.trade import TraderProfile, Portfolio, TradeAction
from app.models.market import MarketState, MarketIndicators, TrendForecast
from app.core.orchestrator import MCPOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class TradeExecution:
    """Record of a trade execution"""
    timestamp: datetime
    action: TradeAction
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    leverage: float


@dataclass
class ProfileMetrics:
    """Performance metrics for a trader profile"""
    profile: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    final_capital: float
    final_returns: float  # Percentage return
    max_drawdown: float  # Maximum drawdown percentage
    avg_volatility: float  # Average portfolio volatility
    constraint_violations: int
    sharpe_ratio: float
    win_rate: float
    avg_profit_per_trade: float
    max_consecutive_losses: int


class ProfileEvaluator:
    """
    Evaluates trader profiles over historical data
    
    Simulates trading with each profile and compares:
    - Returns
    - Risk metrics (drawdown, volatility)
    - Constraint violations
    - Win rate and other statistics
    """
    
    def __init__(self):
        self.orchestrator = MCPOrchestrator()
        
    async def evaluate_profiles(
        self,
        pair: str = "EURUSD",
        initial_capital: float = 10000.0,
        num_periods: int = 30,
        period_days: int = 1
    ) -> Dict[str, ProfileMetrics]:
        """
        Evaluate all trader profiles over a simulated historical period
        
        Args:
            pair: Forex pair to evaluate
            initial_capital: Starting capital for each profile
            num_periods: Number of trading periods to simulate
            period_days: Days per period (for simulation)
            
        Returns:
            Dictionary mapping profile name to metrics
        """
        profiles = [
            TraderProfile.CONSERVATIVE,
            TraderProfile.BALANCED,
            TraderProfile.AGGRESSIVE
        ]
        
        results = {}
        
        for profile in profiles:
            logger.info(f"Evaluating {profile.value} profile...")
            metrics = await self._evaluate_single_profile(
                profile, pair, initial_capital, num_periods, period_days
            )
            results[profile.value] = metrics
            
        return results
    
    async def _evaluate_single_profile(
        self,
        profile: TraderProfile,
        pair: str,
        initial_capital: float,
        num_periods: int,
        period_days: int
    ) -> ProfileMetrics:
        """Evaluate a single trader profile"""
        
        # Initialize portfolio
        portfolio = Portfolio(
            capital=initial_capital,
            open_positions=0,
            total_profit_loss=0.0,
            max_drawdown=0.0
        )
        
        # Track metrics
        trades: List[TradeExecution] = []
        capital_history: List[float] = [initial_capital]
        constraint_violations = 0
        peak_capital = initial_capital
        max_drawdown = 0.0
        volatility_samples: List[float] = []
        consecutive_losses = 0
        max_consecutive_losses = 0
        
        # Simulate trading over periods
        for period in range(num_periods):
            # Generate market state for this period
            market_state = self._generate_market_state(pair, period)
            volatility_samples.append(market_state.indicators.volatility)
            
            # Get recommendation from orchestrator
            try:
                recommendation = await self.orchestrator.recommend_trade(
                    pair=pair,
                    portfolio=portfolio,
                    trader_profile=profile
                )
                
                # Check for constraint violations
                if not recommendation['risk_analysis']['is_valid']:
                    constraint_violations += 1
                    continue
                
                strategy = recommendation['strategy']
                
                # Execute trade if not HOLD
                if strategy['action'] != 'hold':
                    trade = TradeExecution(
                        timestamp=datetime.now(),
                        action=TradeAction(strategy['action']),
                        entry_price=strategy['entry_price'],
                        position_size=strategy['position_size'],
                        stop_loss=strategy['stop_loss'],
                        take_profit=strategy['take_profit'],
                        leverage=strategy['leverage']
                    )
                    trades.append(trade)
                    
                    # Simulate trade outcome (simplified)
                    profit = self._simulate_trade_outcome(
                        trade, market_state, period
                    )
                    
                    portfolio.capital += profit
                    portfolio.total_profit_loss += profit
                    
                    # Track consecutive losses
                    if profit < 0:
                        consecutive_losses += 1
                        max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
                    else:
                        consecutive_losses = 0
                    
                    # Update drawdown
                    if portfolio.capital > peak_capital:
                        peak_capital = portfolio.capital
                    
                    current_drawdown = (peak_capital - portfolio.capital) / peak_capital
                    max_drawdown = max(max_drawdown, current_drawdown)
                    portfolio.max_drawdown = max_drawdown
                
                capital_history.append(portfolio.capital)
                
            except Exception as e:
                logger.error(f"Error in period {period}: {e}")
                continue
        
        # Calculate final metrics
        winning_trades = sum(1 for t in trades if self._is_winning_trade(t))
        losing_trades = len(trades) - winning_trades
        
        final_returns = ((portfolio.capital - initial_capital) / initial_capital) * 100
        avg_volatility = sum(volatility_samples) / len(volatility_samples) if volatility_samples else 0.0
        win_rate = (winning_trades / len(trades) * 100) if trades else 0.0
        avg_profit = portfolio.total_profit_loss / len(trades) if trades else 0.0
        
        # Calculate Sharpe ratio (simplified)
        returns = [(capital_history[i] - capital_history[i-1]) / capital_history[i-1] 
                   for i in range(1, len(capital_history))]
        avg_return = sum(returns) / len(returns) if returns else 0.0
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 0.0
        sharpe_ratio = (avg_return / std_return) if std_return > 0 else 0.0
        
        return ProfileMetrics(
            profile=profile.value,
            total_trades=len(trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            final_capital=portfolio.capital,
            final_returns=final_returns,
            max_drawdown=max_drawdown * 100,  # Convert to percentage
            avg_volatility=avg_volatility,
            constraint_violations=constraint_violations,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            avg_profit_per_trade=avg_profit,
            max_consecutive_losses=max_consecutive_losses
        )
    
    def _generate_market_state(self, pair: str, period: int) -> MarketState:
        """Generate simulated market state for a period"""
        import random
        
        # Create varied market conditions
        # Periods 0-6: Bullish trend
        # Periods 7-13: Bearish trend
        # Periods 14-20: Sideways/Neutral
        # Periods 21+: Mixed
        
        base_price = 1.1000
        
        if period < 7:
            # Bullish trend
            trend_strength = 0.015
            price_change = random.uniform(0.005, trend_strength)
            volatility = 0.006 + random.random() * 0.003
            rsi = 55 + random.random() * 20  # 55-75 (overbought territory)
        elif period < 14:
            # Bearish trend
            trend_strength = -0.015
            price_change = random.uniform(trend_strength, -0.005)
            volatility = 0.008 + random.random() * 0.004
            rsi = 25 + random.random() * 20  # 25-45 (oversold territory)
        elif period < 21:
            # Sideways/Neutral
            price_change = random.uniform(-0.003, 0.003)
            volatility = 0.005 + random.random() * 0.002
            rsi = 45 + random.random() * 10  # 45-55 (neutral)
        else:
            # Mixed conditions
            price_change = random.uniform(-0.01, 0.01)
            volatility = 0.006 + random.random() * 0.005
            rsi = 30 + random.random() * 40  # 30-70 (varied)
        
        # Calculate cumulative price
        current_price = base_price * (1 + price_change * (period / 10))
        
        # Add some noise
        current_price *= (1 + random.uniform(-0.002, 0.002))
        
        indicators = MarketIndicators(
            returns=price_change,
            volatility=volatility,
            sma_20=current_price,
            sma_50=current_price * (1 - price_change * 0.5),  # Trend-following SMA
            rsi=rsi,
            atr=volatility * current_price
        )
        
        return MarketState(
            pair=pair,
            timestamp=datetime.now(),
            current_price=current_price,
            historical_data=[],
            indicators=indicators
        )
    
    def _simulate_trade_outcome(
        self,
        trade: TradeExecution,
        market_state: MarketState,
        period: int
    ) -> float:
        """
        Simulate trade outcome (simplified)
        
        In a real system, this would use actual historical data
        """
        import random
        
        # Simulate whether trade hits SL or TP
        # Use volatility to determine outcome probability
        volatility = market_state.indicators.volatility
        
        # Higher volatility = higher chance of hitting SL
        sl_probability = min(0.4 + volatility * 20, 0.6)
        
        if random.random() < sl_probability:
            # Hit stop loss
            if trade.action == TradeAction.BUY:
                loss = (trade.entry_price - trade.stop_loss) * trade.position_size
            else:  # SELL
                loss = (trade.stop_loss - trade.entry_price) * trade.position_size
            return -abs(loss)
        else:
            # Hit take profit
            if trade.action == TradeAction.BUY:
                profit = (trade.take_profit - trade.entry_price) * trade.position_size
            else:  # SELL
                profit = (trade.entry_price - trade.take_profit) * trade.position_size
            return abs(profit)
    
    def _is_winning_trade(self, trade: TradeExecution) -> bool:
        """Determine if a trade was winning (simplified)"""
        # In real implementation, track actual outcomes
        # For now, use a simple heuristic
        return True  # Placeholder


# Global evaluator instance
_evaluator = None


def get_evaluator() -> ProfileEvaluator:
    """Get or create profile evaluator instance"""
    global _evaluator
    if _evaluator is None:
        _evaluator = ProfileEvaluator()
    return _evaluator
