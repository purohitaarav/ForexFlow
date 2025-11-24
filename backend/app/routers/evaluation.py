"""
Profile Evaluation Router
Handles evaluation and comparison of different trader profiles
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from app.services.profile_evaluator import get_evaluator, ProfileMetrics

router = APIRouter(prefix="/api", tags=["evaluation"])


@router.get("/evaluate_profiles")
async def evaluate_profiles(
    pair: str = Query("EURUSD", description="Forex currency pair to evaluate"),
    initial_capital: float = Query(10000.0, gt=0, description="Starting capital for simulation"),
    num_periods: int = Query(30, ge=10, le=100, description="Number of trading periods to simulate"),
    period_days: int = Query(1, ge=1, le=7, description="Days per trading period")
):
    """
    Evaluate all trader profiles over a simulated historical period
    
    This endpoint runs a backtest simulation for each trader profile
    (conservative, balanced, aggressive) and compares their performance.
    
    **Metrics Calculated**:
    - Final Returns (%)
    - Max Drawdown (%)
    - Average Volatility
    - Constraint Violations
    - Win Rate
    - Sharpe Ratio
    - Total Trades
    - Average Profit per Trade
    
    **Args**:
    - pair: Forex currency pair (e.g., EURUSD, GBPUSD)
    - initial_capital: Starting capital for each profile
    - num_periods: Number of trading periods (default: 30)
    - period_days: Days per period (default: 1)
    
    **Returns**:
    ```json
    {
      "conservative": {
        "profile": "conservative",
        "total_trades": 15,
        "final_returns": 5.2,
        "max_drawdown": 2.1,
        "avg_volatility": 0.008,
        "constraint_violations": 0,
        "win_rate": 60.0,
        "sharpe_ratio": 1.2
      },
      "balanced": {...},
      "aggressive": {...},
      "comparison": {
        "best_returns": "aggressive",
        "lowest_drawdown": "conservative",
        "best_sharpe": "balanced"
      }
    }
    ```
    
    **Example**:
    ```
    GET /api/evaluate_profiles?pair=EURUSD&initial_capital=10000&num_periods=30
    ```
    """
    try:
        evaluator = get_evaluator()
        
        # Run evaluation for all profiles
        results = await evaluator.evaluate_profiles(
            pair=pair,
            initial_capital=initial_capital,
            num_periods=num_periods,
            period_days=period_days
        )
        
        # Convert ProfileMetrics to dict
        results_dict = {
            profile: {
                "profile": metrics.profile,
                "total_trades": metrics.total_trades,
                "winning_trades": metrics.winning_trades,
                "losing_trades": metrics.losing_trades,
                "final_capital": round(metrics.final_capital, 2),
                "final_returns": round(metrics.final_returns, 2),
                "max_drawdown": round(metrics.max_drawdown, 2),
                "avg_volatility": round(metrics.avg_volatility, 4),
                "constraint_violations": metrics.constraint_violations,
                "sharpe_ratio": round(metrics.sharpe_ratio, 3),
                "win_rate": round(metrics.win_rate, 1),
                "avg_profit_per_trade": round(metrics.avg_profit_per_trade, 2),
                "max_consecutive_losses": metrics.max_consecutive_losses
            }
            for profile, metrics in results.items()
        }
        
        # Add comparison summary
        comparison = _generate_comparison(results)
        
        return {
            **results_dict,
            "comparison": comparison,
            "simulation_params": {
                "pair": pair,
                "initial_capital": initial_capital,
                "num_periods": num_periods,
                "period_days": period_days
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating profiles: {str(e)}"
        )


@router.get("/evaluate_profiles/summary")
async def evaluate_profiles_summary(
    pair: str = Query("EURUSD", description="Forex currency pair"),
    num_periods: int = Query(30, ge=10, le=100, description="Number of periods")
):
    """
    Get a quick summary comparison of all trader profiles
    
    Returns a simplified comparison focusing on key metrics:
    - Returns
    - Risk (Drawdown)
    - Win Rate
    
    **Example**:
    ```
    GET /api/evaluate_profiles/summary?pair=EURUSD&num_periods=30
    ```
    """
    try:
        evaluator = get_evaluator()
        
        results = await evaluator.evaluate_profiles(
            pair=pair,
            initial_capital=10000.0,
            num_periods=num_periods,
            period_days=1
        )
        
        summary = {
            profile: {
                "returns": round(metrics.final_returns, 2),
                "max_drawdown": round(metrics.max_drawdown, 2),
                "win_rate": round(metrics.win_rate, 1),
                "sharpe_ratio": round(metrics.sharpe_ratio, 3),
                "total_trades": metrics.total_trades
            }
            for profile, metrics in results.items()
        }
        
        # Determine best profile for each metric
        best_returns = max(results.items(), key=lambda x: x[1].final_returns)
        lowest_drawdown = min(results.items(), key=lambda x: x[1].max_drawdown)
        best_sharpe = max(results.items(), key=lambda x: x[1].sharpe_ratio)
        
        return {
            "profiles": summary,
            "recommendations": {
                "highest_returns": best_returns[0],
                "lowest_risk": lowest_drawdown[0],
                "best_risk_adjusted": best_sharpe[0]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )


def _generate_comparison(results: Dict[str, ProfileMetrics]) -> Dict[str, Any]:
    """Generate comparison summary of all profiles"""
    
    # Find best profile for each metric
    best_returns = max(results.items(), key=lambda x: x[1].final_returns)
    lowest_drawdown = min(results.items(), key=lambda x: x[1].max_drawdown)
    best_sharpe = max(results.items(), key=lambda x: x[1].sharpe_ratio)
    highest_win_rate = max(results.items(), key=lambda x: x[1].win_rate)
    fewest_violations = min(results.items(), key=lambda x: x[1].constraint_violations)
    
    return {
        "best_returns": {
            "profile": best_returns[0],
            "value": round(best_returns[1].final_returns, 2)
        },
        "lowest_drawdown": {
            "profile": lowest_drawdown[0],
            "value": round(lowest_drawdown[1].max_drawdown, 2)
        },
        "best_sharpe_ratio": {
            "profile": best_sharpe[0],
            "value": round(best_sharpe[1].sharpe_ratio, 3)
        },
        "highest_win_rate": {
            "profile": highest_win_rate[0],
            "value": round(highest_win_rate[1].win_rate, 1)
        },
        "fewest_violations": {
            "profile": fewest_violations[0],
            "value": fewest_violations[1].constraint_violations
        },
        "recommendation": _get_overall_recommendation(results)
    }


def _get_overall_recommendation(results: Dict[str, ProfileMetrics]) -> str:
    """Determine overall best profile based on multiple factors"""
    
    # Score each profile (higher is better)
    scores = {}
    
    for profile, metrics in results.items():
        score = 0
        
        # Returns (30% weight)
        score += (metrics.final_returns / 100) * 0.3
        
        # Sharpe ratio (30% weight)
        score += metrics.sharpe_ratio * 0.3
        
        # Inverse drawdown (20% weight) - lower is better
        score += (1 - metrics.max_drawdown / 100) * 0.2
        
        # Win rate (10% weight)
        score += (metrics.win_rate / 100) * 0.1
        
        # Penalty for violations (10% weight)
        violation_penalty = min(metrics.constraint_violations * 0.1, 0.1)
        score -= violation_penalty
        
        scores[profile] = score
    
    best_profile = max(scores.items(), key=lambda x: x[1])
    
    return f"{best_profile[0]} (score: {best_profile[1]:.3f})"
