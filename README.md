# ForexFlow - AI-Powered Forex Trading Simulator

An educational demonstration of Model Context Protocol (MCP) coordinating multiple classical AI methods for Forex trading simulation.

## 🎯 Project Overview

This system showcases how MCP can orchestrate three distinct AI reasoning approaches:

1. **TrendSense** - Probabilistic Reasoning
   - Analyzes historical Forex indicators (returns, volatility, moving averages)
   - Produces probabilistic trend forecasts with uncertainty scores

2. **RiskGuard** - Constraint Satisfaction Problem (CSP)
   - Variables: position size, stop-loss, take-profit, leverage
   - Constraints: max risk per trade, max leverage, minimum capital, drawdown limits
   - Uses CSP techniques like domain filtering and backtracking

3. **OptiTrade** - Search-Based Trade Selection
   - State representation: market snapshot + user portfolio
   - Actions: open, close, adjust trade
   - Uses classical AI search algorithms (greedy best-first or beam search)
   - Produces optimal candidate strategies subject to constraints

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React/Next.js)                │
│  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │  Market Chart    │  │  AI Recommendation Panel        │ │
│  └──────────────────┘  └─────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Orchestrator Endpoint                        │  │
│  │    GET /api/recommend_trade?pair=EURUSD              │  │
│  └──────────────────────────────────────────────────────┘  │
│                             │                               │
│              ┌──────────────┼──────────────┐               │
│              ▼              ▼              ▼               │
│  ┌───────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │  TrendSense   │ │  RiskGuard   │ │  OptiTrade   │     │
│  │  (MCP Tool)   │ │  (MCP Tool)  │ │  (MCP Tool)  │     │
│  │  Probabilistic│ │     CSP      │ │    Search    │     │
│  └───────────────┘ └──────────────┘ └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ForexFlow/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Configuration
│   │   │   └── orchestrator.py  # MCP orchestration logic
│   │   ├── models/
│   │   │   ├── market.py        # Market data models
│   │   │   └── trade.py         # Trade models
│   │   └── mcp_tools/
│   │       ├── trend_sense.py   # Probabilistic reasoning tool
│   │       ├── risk_guard.py    # CSP tool
│   │       └── opti_trade.py    # Search-based tool
│   ├── data/
│   │   └── forex_data.csv       # Historical OHLCV data
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── next.config.js
└── README.md
```

## 🎮 Trader Profiles

The system supports three trader types with different risk parameters:

- **Conservative**: Low risk per trade, low volatility tolerance
- **Balanced**: Moderate risk tolerance
- **Aggressive**: High risk per trade, profit-focused

These parameters affect RiskGuard constraints and OptiTrade scoring.

## 🚀 Getting Started

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🧠 Classical AI Concepts Used

1. **Probabilistic Reasoning** (TrendSense)
   - Bayesian inference on market indicators
   - Uncertainty quantification

2. **Constraint Satisfaction** (RiskGuard)
   - Domain filtering
   - Backtracking search
   - Constraint propagation

3. **Search Algorithms** (OptiTrade)
   - State space representation
   - Greedy best-first search
   - Beam search

4. **Reward Framing** (Evaluation)
   - RL-like reward structure for performance comparison

## 📊 Data Pipeline

- Historical OHLCV (Open, High, Low, Close, Volume) data
- Sliding windows converted to MarketState objects
- Handles volatility, noise, and non-stationarity
- Probabilistic forecasts due to noisy signals

## 🎯 Next Steps

1. Implement MCP tool logic
2. Build FastAPI orchestrator
3. Create React frontend components
4. Integrate real Forex data
5. Add performance comparison across trader profiles
