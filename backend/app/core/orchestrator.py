"""
MCP Orchestrator - Coordinates all three AI reasoning tools

This module orchestrates the execution of:
1. Market Data Fetching (live or fallback)
2. TrendSense (probabilistic reasoning)
3. OptiTrade (search-based optimization)
4. RiskGuard (constraint satisfaction)

to produce comprehensive trade recommendations.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from app.models.market import MarketState, MarketIndicators, OHLCV
from app.models.trade import (
    Portfolio, TraderProfile, TradeResponse, TradeRecommendation, TradeAction
)
from app.mcp_tools.trend_sense import create_trend_sense_tool
from app.mcp_tools.risk_guard import create_risk_guard_tool
from app.mcp_tools.opti_trade import create_opti_trade_tool
from app.services.forex_api import get_forex_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class MCPOrchestrator:
    """
    Orchestrates MCP tools to generate trade recommendations
    
    Execution Flow:
    1. Fetch live MarketState (or use fallback)
    2. TrendSense analyzes market and produces probabilistic forecast
    3. OptiTrade generates candidate strategies
    4. RiskGuard validates each candidate
    5. If rejected, search next best strategy
    6. Return unified response with all analysis
    """
    
    def __init__(self):
        # Initialize MCP tools
        self.trend_sense = create_trend_sense_tool()
        # RiskGuard and OptiTrade are created per-request with trader profile
        
    async def fetch_market_state(self, pair: str) -> MarketState:
        """
        Fetch live market state or fallback to mock data
        
        Args:
            pair: Forex currency pair
            
        Returns:
            MarketState with current price and indicators
        """
        try:
            # Try to fetch live quote
            forex_service = get_forex_service()
            quote = await forex_service.fetch_live_quote(pair)
            
            # Create market state from live data
            # For now, use simple indicators (in production, calculate from historical data)
            indicators = MarketIndicators(
                returns=0.001,  # Placeholder
                volatility=0.008,  # Placeholder
                sma_20=quote['price'],
                sma_50=quote['price'] * 0.998,
                rsi=50.0,
                atr=quote['spread'] * 10
            )
            
            market_state = MarketState(
                pair=pair,
                timestamp=datetime.now(),
                current_price=quote['price'],
                historical_data=[],  # Would fetch historical in production
                indicators=indicators
            )
            
            logger.info(f"Fetched live market state for {pair}: {quote['price']}")
            return market_state
            
        except Exception as e:
            logger.warning(f"Failed to fetch live data for {pair}: {e}. Using fallback.")
            return self._create_fallback_market_state(pair)
    
    def _create_fallback_market_state(self, pair: str) -> MarketState:
        """Create fallback market state with mock data"""
        # Mock data for common pairs
        mock_prices = {
            "EURUSD": 1.1000,
            "GBPUSD": 1.2500,
            "USDJPY": 110.00,
            "AUDUSD": 0.7500,
            "USDCAD": 1.2500,
            "NZDUSD": 0.7000,
            "USDCHF": 0.9200
        }
        
        current_price = mock_prices.get(pair, 1.0000)
        
        indicators = MarketIndicators(
            returns=0.001,
            volatility=0.008,
            sma_20=current_price,
            sma_50=current_price * 0.998,
            rsi=55.0,
            atr=0.0020
        )
        
        return MarketState(
            pair=pair,
            timestamp=datetime.now(),
            current_price=current_price,
            historical_data=[],
            indicators=indicators
        )
        
    async def recommend_trade(
        self,
        pair: str,
        portfolio: Portfolio,
        trader_profile: TraderProfile
    ) -> Dict[str, Any]:
        """
        Generate comprehensive trade recommendation
        
        Pipeline:
        1. Fetch live MarketState (or fallback)
        2. TrendSense → produce trend probabilities
        3. OptiTrade → generate candidate strategies
        4. RiskGuard → validate or reject candidate
        5. If rejected → search next best strategy
        6. Return unified response
        
        Args:
            pair: Forex currency pair
            portfolio: User portfolio state
            trader_profile: Risk profile (conservative/balanced/aggressive)
            
        Returns:
            Unified response with trend, strategy, risk analysis, and final recommendation
        """
        # Step 1: Fetch market state
        market_state = await self.fetch_market_state(pair)
        
        # Step 2: Run TrendSense for probabilistic forecast
        trend_forecast = self.trend_sense.analyze(market_state)
        logger.info(f"TrendSense: {trend_forecast.direction} with {trend_forecast.confidence:.2%} confidence")
        
        # Step 3: Initialize OptiTrade with trader profile
        opti_trade = create_opti_trade_tool(trader_profile)
        
        # Step 4: Initialize RiskGuard
        risk_guard = create_risk_guard_tool()
        
        # Step 5: Run RiskGuard to get initial constraints
        risk_constraints = risk_guard.validate_and_optimize(
            market_state=market_state,
            trend_forecast=trend_forecast,
            portfolio=portfolio,
            trader_profile=trader_profile
        )
        
        logger.info(f"RiskGuard: Valid={risk_constraints.is_valid}, Max Size={risk_constraints.max_position_size}")
        
        # Step 6: Run OptiTrade to find optimal strategy
        trade_recommendation = opti_trade.optimize(
            market_state=market_state,
            trend_forecast=trend_forecast,
            risk_constraints=risk_constraints,
            portfolio=portfolio,
            trader_profile=trader_profile
        )
        
        logger.info(f"OptiTrade: {trade_recommendation.action.value} with score {trade_recommendation.confidence_score:.4f}")
        
        # Step 7: Build unified response
        explanation = self._build_explanation(
            trend_forecast, risk_constraints, trade_recommendation, trader_profile
        )
        
        return {
            "trend": trend_forecast.model_dump(),
            "strategy": {
                "action": trade_recommendation.action.value,
                "entry_price": trade_recommendation.entry_price,
                "position_size": trade_recommendation.position_size,
                "stop_loss": trade_recommendation.stop_loss,
                "take_profit": trade_recommendation.take_profit,
                "leverage": trade_recommendation.leverage,
                "expected_profit": trade_recommendation.expected_profit,
                "risk_reward_ratio": trade_recommendation.risk_reward_ratio,
                "confidence_score": trade_recommendation.confidence_score
            },
            "risk_analysis": {
                "is_valid": risk_constraints.is_valid,
                "max_position_size": risk_constraints.max_position_size,
                "risk_amount": risk_constraints.risk_amount,
                "constraint_violations": risk_constraints.constraint_violations
            },
            "final_recommendation": {
                "action": trade_recommendation.action.value,
                "pair": pair,
                "trader_profile": trader_profile.value,
                "timestamp": datetime.now().isoformat()
            },
            "explanation": explanation,
            "market_data": {
                "pair": market_state.pair,
                "current_price": market_state.current_price,
                "volatility": market_state.indicators.volatility
            }
        }
    
    def _build_explanation(
        self,
        trend_forecast,
        risk_constraints,
        trade_recommendation,
        trader_profile: TraderProfile
    ) -> str:
        """Build human-readable explanation of the recommendation"""
        
        explanation_parts = []
        
        # Market Analysis
        explanation_parts.append(f"**Market Analysis ({trader_profile.value} profile)**")
        explanation_parts.append(f"Trend: {trend_forecast.direction} with {trend_forecast.confidence:.1%} confidence")
        explanation_parts.append(f"Probabilities: ↑{trend_forecast.probability_up:.1%} ↓{trend_forecast.probability_down:.1%} →{trend_forecast.probability_neutral:.1%}")
        
        # Risk Assessment
        explanation_parts.append(f"\n**Risk Assessment**")
        if risk_constraints.is_valid:
            explanation_parts.append(f"✓ Risk constraints satisfied")
            explanation_parts.append(f"Max Position: {risk_constraints.max_position_size:.0f} units")
            explanation_parts.append(f"Risk Amount: ${risk_constraints.risk_amount:.2f}")
        else:
            explanation_parts.append(f"✗ Risk constraints violated:")
            for violation in risk_constraints.constraint_violations:
                explanation_parts.append(f"  - {violation}")
        
        # Strategy Recommendation
        explanation_parts.append(f"\n**Strategy Recommendation**")
        explanation_parts.append(f"Action: {trade_recommendation.action.value.upper()}")
        
        if trade_recommendation.action != TradeAction.HOLD:
            explanation_parts.append(f"Position Size: {trade_recommendation.position_size:.0f} units")
            explanation_parts.append(f"Entry: {trade_recommendation.entry_price:.4f}")
            explanation_parts.append(f"Stop Loss: {trade_recommendation.stop_loss:.4f}")
            explanation_parts.append(f"Take Profit: {trade_recommendation.take_profit:.4f}")
            explanation_parts.append(f"Risk/Reward: {trade_recommendation.risk_reward_ratio:.2f}:1")
            explanation_parts.append(f"Expected Profit: ${trade_recommendation.expected_profit:.2f}")
        
        explanation_parts.append(f"\n**Reasoning**")
        explanation_parts.append(trade_recommendation.reasoning)
        
        return "\n".join(explanation_parts)
    
    def get_tool_status(self) -> Dict[str, str]:
        """Get status of all MCP tools"""
        return {
            "trend_sense": "active",
            "risk_guard": "active",
            "opti_trade": "active",
            "orchestrator": "active"
        }


# Global orchestrator instance
orchestrator = MCPOrchestrator()

