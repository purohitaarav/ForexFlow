"""
OptiTrade MCP Tool - Search-Based Trade Optimization

This tool uses classical AI search algorithms to find optimal trading strategies
given market state, trend forecasts, and risk constraints.

Classical AI Concepts:
- State space search
- Beam search with multi-depth exploration
- Trader-profile-specific heuristic evaluation functions
- Reasoning trace generation
"""
import numpy as np
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from app.models.trade import TradeRecommendation, TradeAction, Portfolio, TraderProfile
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
    portfolio_state: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    depth: int = 0
    parent: Optional['SearchState'] = None
    reasoning: str = ""


class OptiTradeTool:
    """
    MCP Tool for search-based trade optimization
    
    State Space:
    - Portfolio state + recent market state
    - Possible trade actions with parameters
    
    Actions:
    - open_trade (BUY/SELL with size/SL/TP)
    - close_trade (close existing position)
    - adjust_size (modify position size)
    
    Search Algorithm:
    - Beam search with configurable width and depth
    - Trader-profile-specific heuristics
    - Reasoning trace for explainability
    """
    
    def __init__(self, trader_profile: TraderProfile = TraderProfile.BALANCED):
        self.name = "opti_trade"
        self.description = "Search-based trade strategy optimization"
        self.beam_width = settings.SEARCH_BEAM_WIDTH
        self.max_depth = settings.SEARCH_MAX_DEPTH
        self.trader_profile = trader_profile
        self.explored_states: List[SearchState] = []
        self.reasoning_trace: List[str] = []
        
    def optimize(
        self,
        market_state: MarketState,
        trend_forecast: TrendForecast,
        risk_constraints: RiskConstraints,
        portfolio: Portfolio,
        trader_profile: TraderProfile = TraderProfile.BALANCED
    ) -> TradeRecommendation:
        """
        Find optimal trade recommendation using beam search
        
        Args:
            market_state: Current market state
            trend_forecast: Probabilistic trend forecast
            risk_constraints: Validated risk parameters
            portfolio: Current portfolio state
            trader_profile: Trader risk profile for heuristic tuning
            
        Returns:
            TradeRecommendation with optimal strategy and reasoning trace
        """
        self.trader_profile = trader_profile
        self.explored_states = []
        self.reasoning_trace = []
        
        start_time = time.time()
        
        # Check if risk constraints are valid
        if not risk_constraints.is_valid:
            return self._create_hold_recommendation(
                market_state,
                "Risk constraints not satisfied"
            )
        
        # Generate initial states (possible actions)
        initial_states = self._generate_initial_states(
            market_state, trend_forecast, risk_constraints, portfolio
        )
        
        self.reasoning_trace.append(f"Generated {len(initial_states)} initial candidate states")
        
        # Run beam search to find optimal strategy
        best_state = self._beam_search(
            initial_states, market_state, trend_forecast, portfolio, risk_constraints
        )
        
        execution_time = (time.time() - start_time) * 1000  # ms
        self.reasoning_trace.append(f"Search completed in {execution_time:.2f}ms")
        self.reasoning_trace.append(f"Best state score: {best_state.score:.4f}")
        
        # Convert best state to trade recommendation
        return self._state_to_recommendation(
            best_state, market_state, trend_forecast
        )
    
    def _generate_initial_states(
        self,
        market_state: MarketState,
        trend_forecast: TrendForecast,
        risk_constraints: RiskConstraints,
        portfolio: Portfolio
    ) -> List[SearchState]:
        """
        Generate initial search states (possible actions)
        
        Actions:
        - open_trade (BUY): if bullish trend
        - open_trade (SELL): if bearish trend
        - HOLD: always available
        - close_trade: if open positions exist
        """
        states = []
        current_price = market_state.current_price
        
        portfolio_dict = {
            "capital": portfolio.capital,
            "open_positions": portfolio.open_positions,
            "total_profit_loss": portfolio.total_profit_loss,
            "max_drawdown": portfolio.max_drawdown
        }
        
        # Generate multiple BUY states with varying position sizes (if bullish)
        if trend_forecast.probability_up > 0.3:
            for size_multiplier in [1.0, 0.75, 0.5]:
                buy_state = SearchState(
                    action=TradeAction.BUY,
                    entry_price=current_price,
                    position_size=risk_constraints.max_position_size * size_multiplier,
                    stop_loss=risk_constraints.stop_loss,
                    take_profit=risk_constraints.take_profit,
                    leverage=risk_constraints.leverage,
                    portfolio_state=portfolio_dict.copy(),
                    depth=0,
                    reasoning=f"Open BUY position ({size_multiplier*100:.0f}% of max size)"
                )
                states.append(buy_state)
        
        # Generate multiple SELL states with varying position sizes (if bearish)
        if trend_forecast.probability_down > 0.3:
            # For SELL, stop loss and take profit are inverted
            sl_pct = (risk_constraints.stop_loss - current_price) / current_price
            tp_pct = (risk_constraints.take_profit - current_price) / current_price
            
            sell_stop_loss = current_price * (1 - sl_pct)  # Above entry
            sell_take_profit = current_price * (1 - tp_pct)  # Below entry
            
            for size_multiplier in [1.0, 0.75, 0.5]:
                sell_state = SearchState(
                    action=TradeAction.SELL,
                    entry_price=current_price,
                    position_size=risk_constraints.max_position_size * size_multiplier,
                    stop_loss=sell_stop_loss,
                    take_profit=sell_take_profit,
                    leverage=risk_constraints.leverage,
                    portfolio_state=portfolio_dict.copy(),
                    depth=0,
                    reasoning=f"Open SELL position ({size_multiplier*100:.0f}% of max size)"
                )
                states.append(sell_state)
        
        # HOLD state (always an option)
        hold_state = SearchState(
            action=TradeAction.HOLD,
            entry_price=current_price,
            position_size=0.0,
            stop_loss=current_price,
            take_profit=current_price,
            leverage=1.0,
            portfolio_state=portfolio_dict.copy(),
            depth=0,
            reasoning="Hold current position - no trade"
        )
        states.append(hold_state)
        
        # CLOSE state (if there are open positions)
        if portfolio.open_positions > 0:
            close_state = SearchState(
                action=TradeAction.CLOSE,
                entry_price=current_price,
                position_size=0.0,
                stop_loss=current_price,
                take_profit=current_price,
                leverage=1.0,
                portfolio_state=portfolio_dict.copy(),
                depth=0,
                reasoning="Close existing positions"
            )
            states.append(close_state)
        
        return states
    
    def _beam_search(
        self,
        initial_states: List[SearchState],
        market_state: MarketState,
        trend_forecast: TrendForecast,
        portfolio: Portfolio,
        risk_constraints: RiskConstraints
    ) -> SearchState:
        """
        Beam search to find optimal trade strategy
        
        Maintains top-k candidates at each level and explores their successors
        """
        # Current beam (top-k states)
        beam = initial_states
        
        # Evaluate all initial states
        for state in beam:
            state.score = self._evaluate_state(
                state, market_state, trend_forecast, portfolio
            )
            self.explored_states.append(state)
        
        # Sort by score (descending) and keep top beam_width
        beam.sort(key=lambda s: s.score, reverse=True)
        beam = beam[:self.beam_width]
        
        self.reasoning_trace.append(f"Depth 0: Evaluated {len(initial_states)} states, kept top {len(beam)}")
        
        # Iterative deepening up to max_depth
        for depth in range(1, self.max_depth + 1):
            # Generate successors for each state in beam
            successors = []
            for state in beam:
                new_states = self._generate_successors(
                    state, market_state, risk_constraints, depth
                )
                successors.extend(new_states)
            
            if not successors:
                break
            
            # Evaluate all successors
            for state in successors:
                state.score = self._evaluate_state(
                    state, market_state, trend_forecast, portfolio
                )
                self.explored_states.append(state)
            
            # Sort and prune to beam width
            successors.sort(key=lambda s: s.score, reverse=True)
            beam = successors[:self.beam_width]
            
            self.reasoning_trace.append(f"Depth {depth}: Evaluated {len(successors)} states, kept top {len(beam)}")
        
        # Return best state from final beam
        if beam:
            return beam[0]
        
        # Fallback to HOLD
        return SearchState(
            action=TradeAction.HOLD,
            entry_price=market_state.current_price,
            position_size=0.0,
            stop_loss=market_state.current_price,
            take_profit=market_state.current_price,
            leverage=1.0,
            score=0.0,
            reasoning="Fallback HOLD"
        )
    
    def _generate_successors(
        self,
        state: SearchState,
        market_state: MarketState,
        risk_constraints: RiskConstraints,
        depth: int
    ) -> List[SearchState]:
        """
        Generate successor states from current state
        
        Actions:
        - adjust_size: Increase/decrease position size
        - Adjust SL/TP levels
        """
        successors = []
        
        # If current state is HOLD, no successors (terminal)
        if state.action == TradeAction.HOLD or state.action == TradeAction.CLOSE:
            return successors
        
        # Adjust position size (±25%)
        for size_adj in [1.25, 0.75]:
            new_size = state.position_size * size_adj
            if new_size <= risk_constraints.max_position_size and new_size >= 100:
                successor = SearchState(
                    action=state.action,
                    entry_price=state.entry_price,
                    position_size=new_size,
                    stop_loss=state.stop_loss,
                    take_profit=state.take_profit,
                    leverage=state.leverage,
                    portfolio_state=state.portfolio_state.copy(),
                    depth=depth,
                    parent=state,
                    reasoning=f"Adjust size to {new_size:.0f} units"
                )
                successors.append(successor)
        
        return successors
    
    def _evaluate_state(
        self,
        state: SearchState,
        market_state: MarketState,
        trend_forecast: TrendForecast,
        portfolio: Portfolio
    ) -> float:
        """
        Heuristic evaluation function for search states
        
        Trader-profile-specific:
        - Conservative: Penalize volatility and drawdown
        - Balanced: Balance profit and risk
        - Aggressive: Weight profit highly
        """
        # HOLD action has neutral score
        if state.action == TradeAction.HOLD:
            return 0.0
        
        # CLOSE action has small positive score (exit risk)
        if state.action == TradeAction.CLOSE:
            return 0.1
        
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
        
        # Volatility penalty (for conservative traders)
        volatility = market_state.indicators.volatility
        volatility_penalty = volatility * 10  # Normalize
        
        # Drawdown penalty
        drawdown_penalty = portfolio.max_drawdown
        
        # Trader-profile-specific weights
        if self.trader_profile == TraderProfile.CONSERVATIVE:
            # Conservative: Penalize volatility and drawdown heavily
            score = (
                0.25 * expected_profit +
                0.35 * risk_reward +
                0.15 * trend_alignment +
                0.10 * confidence -
                0.10 * volatility_penalty -
                0.05 * drawdown_penalty
            )
        elif self.trader_profile == TraderProfile.AGGRESSIVE:
            # Aggressive: Weight profit highly, ignore volatility
            score = (
                0.60 * expected_profit +
                0.20 * risk_reward +
                0.15 * trend_alignment +
                0.05 * confidence
            )
        else:  # BALANCED
            # Balanced: Equal weighting
            score = (
                0.35 * expected_profit +
                0.30 * risk_reward +
                0.20 * trend_alignment +
                0.10 * confidence -
                0.05 * volatility_penalty
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
        if state.action == TradeAction.HOLD or state.action == TradeAction.CLOSE:
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
        if state.action == TradeAction.HOLD or state.action == TradeAction.CLOSE:
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
            reasoning = f"Bullish trend ({trend_forecast.confidence:.1%} confidence). {state.reasoning}"
        elif state.action == TradeAction.SELL:
            expected_profit = (state.entry_price - state.take_profit) * state.position_size
            reasoning = f"Bearish trend ({trend_forecast.confidence:.1%} confidence). {state.reasoning}"
        else:
            expected_profit = 0.0
            reasoning = f"No strong trend signal. {state.reasoning}"
        
        # Add reasoning trace
        reasoning += f"\n\nSearch trace:\n" + "\n".join(self.reasoning_trace)
        
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
            risk_reward_ratio=risk_reward * 3.0 if risk_reward > 0 else 0.0,  # Denormalize
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
def create_opti_trade_tool(trader_profile: TraderProfile = TraderProfile.BALANCED) -> OptiTradeTool:
    """Factory function to create OptiTrade tool instance"""
    return OptiTradeTool(trader_profile)
