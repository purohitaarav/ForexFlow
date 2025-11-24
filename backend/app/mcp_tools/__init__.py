"""
MCP Tools Package

Exports all MCP tool functions and schemas
"""
from app.mcp_tools.predict_trend import (
    predict_trend,
    predict_trend_batch,
    get_predict_trend_schema,
    TOOL_METADATA as PREDICT_TREND_METADATA
)

from app.mcp_tools.check_constraints import (
    check_constraints,
    check_constraints_batch,
    validate_constraints_only,
    get_check_constraints_schema,
    TOOL_METADATA as CHECK_CONSTRAINTS_METADATA
)

from app.mcp_tools.find_best_trade import (
    find_best_trade,
    find_best_trade_batch,
    evaluate_trade_state,
    get_find_best_trade_schema,
    TOOL_METADATA as FIND_BEST_TRADE_METADATA
)

from app.mcp_tools.schemas import (
    PredictTrendInput,
    PredictTrendOutput,
    CheckConstraintsInput,
    CheckConstraintsOutput,
    FindBestTradeInput,
    FindBestTradeOutput,
    MCPPipelineInput,
    MCPPipelineOutput,
    TrendDirection,
    TradeActionEnum
)


# Tool registry
MCP_TOOLS = {
    "predict_trend": {
        "function": predict_trend,
        "batch_function": predict_trend_batch,
        "schema_function": get_predict_trend_schema,
        "metadata": PREDICT_TREND_METADATA
    },
    "check_constraints": {
        "function": check_constraints,
        "batch_function": check_constraints_batch,
        "schema_function": get_check_constraints_schema,
        "metadata": CHECK_CONSTRAINTS_METADATA
    },
    "find_best_trade": {
        "function": find_best_trade,
        "batch_function": find_best_trade_batch,
        "schema_function": get_find_best_trade_schema,
        "metadata": FIND_BEST_TRADE_METADATA
    }
}


def get_all_tool_schemas():
    """Get schemas for all MCP tools"""
    return {
        name: tool["schema_function"]()
        for name, tool in MCP_TOOLS.items()
    }


def get_all_tool_metadata():
    """Get metadata for all MCP tools"""
    return {
        name: tool["metadata"]
        for name, tool in MCP_TOOLS.items()
    }


__all__ = [
    # Tool functions
    "predict_trend",
    "predict_trend_batch",
    "check_constraints",
    "check_constraints_batch",
    "validate_constraints_only",
    "find_best_trade",
    "find_best_trade_batch",
    "evaluate_trade_state",
    
    # Schema functions
    "get_predict_trend_schema",
    "get_check_constraints_schema",
    "get_find_best_trade_schema",
    "get_all_tool_schemas",
    "get_all_tool_metadata",
    
    # Schemas
    "PredictTrendInput",
    "PredictTrendOutput",
    "CheckConstraintsInput",
    "CheckConstraintsOutput",
    "FindBestTradeInput",
    "FindBestTradeOutput",
    "MCPPipelineInput",
    "MCPPipelineOutput",
    "TrendDirection",
    "TradeActionEnum",
    
    # Registry
    "MCP_TOOLS"
]
