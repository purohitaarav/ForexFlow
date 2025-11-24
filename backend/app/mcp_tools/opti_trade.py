"""
OptiTrade MCP Tool - Search-Based Trade Optimization

This tool uses classical AI search algorithms to find optimal trading strategies
given market state, trend forecasts, and risk constraints.

Classical AI Concepts:
- State space search
- Greedy best-first search
- Beam search
- Heuristic evaluation functions
"""
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from app.models.trade import TradeRecommendation, TradeAction, Portfolio
from app.models.market import MarketState, TrendForecast
from app.models.trade import RiskConstraints
from app.core.config import settings


@dataclass
class SearchState:
    """State representation for search algorithm"""
    action: TradeAction
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    leverage: float
    score: float = 0.0
    parent: Optional['SearchState'] = None


class OptiTradeTool:
    """
    MCP Tool for search-based trade optimization
    
    State Space:
    - Current market conditions
    - Portfolio state
    - Possible trade actions
    
    Actions:
    - BUY with various parameters
    - SELL with various parameters
    - HOLD (no action)
    - CLOSE existing positions
    
    Search Algorithm:
    - Beam search to explore multiple candidate strategies
    - Greedy best-first for quick optimization
    - Heuristic evaluation based on expected profit and risk
    """
    
    def __init__(self):
        self.name = "opti_trade"
        self.description = "Search-based trade strategy optimization"
        self.beam_width = settings.SEARCH_BEAM_WIDTH
        self.max_depth = settings.SEARCH_MAX_DEPTH
        
    def optimize(
        self,
        market_state: MarketState,
        trend_forecast: TrendForecast,
        risk_constraints: RiskConstraints,
        portfolio: Portfolio
    ) -> TradeRecommendation:
        """
        Find optimal trade recommendation using search
        
        Args:
            market_state: Current market state
            trend_forecast: Probabilistic trend forecast
            risk_constraints: Validated risk parameters
            portfolio: Current portfolio state
            
        Returns:
            TradeRecommendation with optimal strategy
        """
        # Check if risk constraints are valid
        if not risk_constraints.is_valid:
            return self._create_hold_recommendation(
                market_state,
                "Risk constraints not satisfied"
            )
        
        # Generate initial states (possible actions)
        initial_states = self._generate_initial_states(
            market_state, trend_forecast, risk_constraints
        )
        
        # Run beam search to find optimal strategy
        best_state = self._beam_search(
            initial_states, market_state, trend_forecast, portfolio
        )
        
        # Convert best state to trade recommendation
        return self._state_to_recommendation(
            best_state, market_state, trend_forecast
        )
    
    def _generate_initial_states(
        self,
        market_state: MarketState,
        trend_forecast: TrendForecast,
        risk_constraints: RiskConstraints
    ) -> List[SearchState]:
        """
        Generate initial search states (possible actions)
        
        Based on trend forecast, generate candidate BUY/SELL actions
        with parameters from risk constraints
        """
        states = []
        current_price = market_state.current_price
        
        # TODO: Generate multiple candidate states with varying parameters
        # For now, create simple candidates based on trend direction
        
        # BUY state (if bullish trend)
        if trend_forecast.probability_up > 0.4:
            buy_state = SearchState(
                action=TradeAction.BUY,
                entry_price=current_price,
                position_size=risk_constraints.max_position_size,
                stop_loss=risk_constraints.stop_loss,
                take_profit=risk_constraints.take_profit,
                leverage=risk_constraints.leverage
            )
            states.append(buy_state)
        
        # SELL state (if bearish trend)
        if trend_forecast.probability_down > 0.4:
            # For SELL, stop loss and take profit are inverted
            sell_stop_loss = current_price * (1 + 0.02)  # Above entry
            sell_take_profit = current_price * (1 - 0.04)  # Below entry
            
            sell_state = SearchState(
                action=TradeAction.SELL,
                entry_price=current_price,
                position_size=risk_constraints.max_position_size,
                stop_loss=sell_stop_loss,
                take_profit=sell_take_profit,
                leverage=risk_constraints.leverage
            )
            states.append(sell_state)
        
        # HOLD state (always an option)
        hold_state = SearchState(
            action=TradeAction.HOLD,
            entry_price=current_price,
            position_size=0.0,
            stop_loss=current_price,
            take_profit=current_price,
            leverage=1.0
        )
        states.append(hold_state)
        
        return states
    
    def _beam_search(
        self,
        initial_states: List[SearchState],
        market_state: MarketState,
        trend_forecast: TrendForecast,
        portfolio: Portfolio
    ) -> SearchState:
        """
        Beam search to find optimal trade strategy
        
        Maintains top-k candidates at each level and explores their successors
        """
        # TODO: Implement full beam search with multiple depth levels
        # For now, use single-level greedy selection
        
        # Evaluate all initial states
        for state in initial_states:
            state.score = self._evaluate_state(
                state, market_state, trend_forecast, portfolio
            )
        
        # Sort by score (descending)
        initial_states.sort(key=lambda s: s.score, reverse=True)
        
        # Return best state
        if initial_states:
            return initial_states[0]
        
        # Fallback to HOLD
        return SearchState(
            action=TradeAction.HOLD,
            entry_price=market_state.current_price,
            position_size=0.0,
            stop_loss=market_state.current_price,
            take_profit=market_state.current_price,
            leverage=1.0,
            score=0.0
        )
    
    def _evaluate_state(
        self,
        state: SearchState,
        market_state: MarketState,
        trend_forecast: TrendForecast,
        portfolio: Portfolio
    ) -> float:
        """
        Heuristic evaluation function for search states
        
        Combines:
        - Expected profit (from trend forecast)
        - Risk-reward ratio
        - Trend confidence
        - Portfolio constraints
        """
        # HOLD action has neutral score
        if state.action == TradeAction.HOLD:
            return 0.0
        
        # Calculate expected profit
        expected_profit = self._calculate_expected_profit(
            state, trend_forecast
        )
        
        # Calculate risk-reward ratio
        risk_reward = self._calculate_risk_reward(state)
        
        # Trend alignment score
        trend_alignment = self._calculate_trend_alignment(
            state, trend_forecast
        )
        
        # Confidence score
        confidence = trend_forecast.confidence
        
        # Combined heuristic score
        # TODO: Tune weights based on performance
        score = (
            0.4 * expected_profit +
            0.3 * risk_reward +
            0.2 * trend_alignment +
            0.1 * confidence
        )
        
        return score
    
    def _calculate_expected_profit(
        self,
        state: SearchState,
        trend_forecast: TrendForecast
    ) -> float:
        """Calculate expected profit for a trade state"""
        if state.action == TradeAction.BUY:
            # Expected profit if price goes up
            profit_if_up = (state.take_profit - state.entry_price) * state.position_size
            loss_if_down = (state.entry_price - state.stop_loss) * state.position_size
            
            expected = (
                trend_forecast.probability_up * profit_if_up -
                trend_forecast.probability_down * loss_if_down
            )
        elif state.action == TradeAction.SELL:
            # Expected profit if price goes down
            profit_if_down = (state.entry_price - state.take_profit) * state.position_size
            loss_if_up = (state.stop_loss - state.entry_price) * state.position_size
            
            expected = (
                trend_forecast.probability_down * profit_if_down -
                trend_forecast.probability_up * loss_if_up
            )
        else:
            expected = 0.0
        
        # Normalize to [0, 1] range
        return np.tanh(expected / 1000.0)
    
    def _calculate_risk_reward(self, state: SearchState) -> float:
        """Calculate risk-reward ratio"""
        if state.action == TradeAction.HOLD:
            return 0.0
        
        if state.action == TradeAction.BUY:
            risk = abs(state.entry_price - state.stop_loss)
            reward = abs(state.take_profit - state.entry_price)
        else:  # SELL
            risk = abs(state.stop_loss - state.entry_price)
            reward = abs(state.entry_price - state.take_profit)
        
        if risk == 0:
            return 0.0
        
        ratio = reward / risk
        
        # Normalize to [0, 1], with 3:1 ratio = 1.0
        return min(ratio / 3.0, 1.0)
    
    def _calculate_trend_alignment(
        self,
        state: SearchState,
        trend_forecast: TrendForecast
    ) -> float:
        """Calculate how well the action aligns with trend forecast"""
        if state.action == TradeAction.HOLD:
            return 0.5  # Neutral
        
        if state.action == TradeAction.BUY:
            return trend_forecast.probability_up
        else:  # SELL
            return trend_forecast.probability_down
    
    def _state_to_recommendation(
        self,
        state: SearchState,
        market_state: MarketState,
        trend_forecast: TrendForecast
    ) -> TradeRecommendation:
        """Convert search state to trade recommendation"""
        # Calculate expected profit
        if state.action == TradeAction.BUY:
            expected_profit = (state.take_profit - state.entry_price) * state.position_size
            reasoning = f"Bullish trend detected with {trend_forecast.confidence:.1%} confidence"
        elif state.action == TradeAction.SELL:
            expected_profit = (state.entry_price - state.take_profit) * state.position_size
            reasoning = f"Bearish trend detected with {trend_forecast.confidence:.1%} confidence"
        else:
            expected_profit = 0.0
            reasoning = "No strong trend signal - holding position"
        
        # Calculate risk-reward ratio
        risk_reward = self._calculate_risk_reward(state)
        
        return TradeRecommendation(
            action=state.action,
            pair=market_state.pair,
            entry_price=state.entry_price,
            position_size=state.position_size,
            stop_loss=state.stop_loss,
            take_profit=state.take_profit,
            leverage=state.leverage,
            expected_profit=expected_profit,
            risk_reward_ratio=risk_reward * 3.0,  # Denormalize
            confidence_score=state.score,
            reasoning=reasoning
        )
    
    def _create_hold_recommendation(
        self,
        market_state: MarketState,
        reason: str
    ) -> TradeRecommendation:
        """Create a HOLD recommendation"""
        return TradeRecommendation(
            action=TradeAction.HOLD,
            pair=market_state.pair,
            entry_price=market_state.current_price,
            position_size=0.0,
            stop_loss=market_state.current_price,
            take_profit=market_state.current_price,
            leverage=1.0,
            expected_profit=0.0,
            risk_reward_ratio=0.0,
            confidence_score=0.0,
            reasoning=reason
        )


# MCP Tool Interface
def create_opti_trade_tool() -> OptiTradeTool:
    """Factory function to create OptiTrade tool instance"""
    return OptiTradeTool()
