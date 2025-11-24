"""
MCP Orchestrator - Coordinates all three AI reasoning tools

This module orchestrates the execution of:
1. TrendSense (probabilistic reasoning)
2. RiskGuard (constraint satisfaction)
3. OptiTrade (search-based optimization)

to produce comprehensive trade recommendations.
"""
from typing import Dict, Any
from datetime import datetime
from app.models.market import MarketState
from app.models.trade import (
    Portfolio, TraderProfile, TradeResponse, TradeRecommendation
)
from app.mcp_tools.trend_sense import create_trend_sense_tool
from app.mcp_tools.risk_guard import create_risk_guard_tool
from app.mcp_tools.opti_trade import create_opti_trade_tool


class MCPOrchestrator:
    """
    Orchestrates MCP tools to generate trade recommendations
    
    Execution Flow:
    1. TrendSense analyzes market and produces probabilistic forecast
    2. RiskGuard validates constraints using CSP
    3. OptiTrade searches for optimal strategy
    4. Results are combined into final recommendation
    """
    
    def __init__(self):
        # Initialize MCP tools
        self.trend_sense = create_trend_sense_tool()
        self.risk_guard = create_risk_guard_tool()
        self.opti_trade = create_opti_trade_tool()
        
    async def recommend_trade(
        self,
        market_state: MarketState,
        portfolio: Portfolio,
        trader_profile: TraderProfile
    ) -> TradeResponse:
        """
        Generate comprehensive trade recommendation
        
        Args:
            market_state: Current market state with indicators
            portfolio: User portfolio state
            trader_profile: Risk profile (conservative/balanced/aggressive)
            
        Returns:
            TradeResponse with recommendation and supporting analysis
        """
        # Step 1: Run TrendSense for probabilistic forecast
        trend_forecast = self.trend_sense.analyze(market_state)
        
        # Step 2: Run RiskGuard to validate constraints
        risk_constraints = self.risk_guard.validate_and_optimize(
            market_state=market_state,
            trend_forecast=trend_forecast,
            portfolio=portfolio,
            trader_profile=trader_profile
        )
        
        # Step 3: Run OptiTrade to find optimal strategy
        trade_recommendation = self.opti_trade.optimize(
            market_state=market_state,
            trend_forecast=trend_forecast,
            risk_constraints=risk_constraints,
            portfolio=portfolio
        )
        
        # Combine results into response
        return TradeResponse(
            recommendation=trade_recommendation,
            trend_forecast=trend_forecast.model_dump(),
            risk_constraints=risk_constraints,
            timestamp=datetime.now()
        )
    
    def get_tool_status(self) -> Dict[str, str]:
        """Get status of all MCP tools"""
        return {
            "trend_sense": "active",
            "risk_guard": "active",
            "opti_trade": "active"
        }


# Global orchestrator instance
orchestrator = MCPOrchestrator()
