# ForexFlow Architecture

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React/Next.js UI]
        Chart[Market Chart Component]
        Panel[Recommendation Panel]
    end
    
    subgraph "API Layer"
        API[FastAPI Backend]
        Routes[API Routes]
        Orch[MCP Orchestrator]
    end
    
    subgraph "MCP Tools Layer"
        TS[TrendSense<br/>Probabilistic Reasoning]
        RG[RiskGuard<br/>CSP Solver]
        OT[OptiTrade<br/>Search Algorithm]
    end
    
    subgraph "Data Layer"
        Market[Market Data<br/>OHLCV + Indicators]
        Portfolio[Portfolio State]
        Profile[Trader Profile]
    end
    
    UI --> Chart
    UI --> Panel
    UI --> Routes
    Routes --> Orch
    
    Orch --> TS
    Orch --> RG
    Orch --> OT
    
    Market --> TS
    Market --> RG
    Market --> OT
    
    Portfolio --> RG
    Portfolio --> OT
    
    Profile --> RG
    Profile --> OT
    
    TS -.Forecast.-> RG
    TS -.Forecast.-> OT
    RG -.Constraints.-> OT
    
    OT -.Recommendation.-> Orch
    Orch --> Routes
    Routes --> Panel
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Orchestrator
    participant TrendSense
    participant RiskGuard
    participant OptiTrade
    
    User->>Frontend: Select Pair & Profile
    Frontend->>API: GET /api/recommend_trade
    API->>Orchestrator: recommend_trade()
    
    Note over Orchestrator: Step 1: Analyze Market
    Orchestrator->>TrendSense: analyze(market_state)
    TrendSense-->>TrendSense: Calculate probabilities
    TrendSense-->>TrendSense: Bayesian inference
    TrendSense-->>Orchestrator: TrendForecast
    
    Note over Orchestrator: Step 2: Validate Constraints
    Orchestrator->>RiskGuard: validate_and_optimize()
    RiskGuard-->>RiskGuard: Define CSP variables
    RiskGuard-->>RiskGuard: Apply constraints
    RiskGuard-->>RiskGuard: Backtracking search
    RiskGuard-->>Orchestrator: RiskConstraints
    
    Note over Orchestrator: Step 3: Optimize Strategy
    Orchestrator->>OptiTrade: optimize()
    OptiTrade-->>OptiTrade: Generate states
    OptiTrade-->>OptiTrade: Beam search
    OptiTrade-->>OptiTrade: Evaluate heuristics
    OptiTrade-->>Orchestrator: TradeRecommendation
    
    Orchestrator->>API: TradeResponse
    API->>Frontend: JSON Response
    Frontend->>User: Display Recommendation
```

## MCP Coordination Pipeline

```mermaid
flowchart LR
    subgraph Input
        MD[Market Data]
        PF[Portfolio]
        TP[Trader Profile]
    end
    
    subgraph "MCP Tool 1: TrendSense"
        direction TB
        TS1[Historical Data]
        TS2[Calculate Indicators]
        TS3[Probabilistic Model]
        TS4[Trend Forecast]
        
        TS1 --> TS2 --> TS3 --> TS4
    end
    
    subgraph "MCP Tool 2: RiskGuard"
        direction TB
        RG1[Define Variables]
        RG2[Set Constraints]
        RG3[CSP Solver]
        RG4[Risk Parameters]
        
        RG1 --> RG2 --> RG3 --> RG4
    end
    
    subgraph "MCP Tool 3: OptiTrade"
        direction TB
        OT1[Generate States]
        OT2[Beam Search]
        OT3[Evaluate Heuristics]
        OT4[Best Strategy]
        
        OT1 --> OT2 --> OT3 --> OT4
    end
    
    subgraph Output
        Rec[Trade Recommendation]
    end
    
    MD --> TS1
    MD --> RG1
    MD --> OT1
    
    PF --> RG1
    PF --> OT1
    
    TP --> RG2
    TP --> OT1
    
    TS4 -.Probability Distribution.-> RG3
    TS4 -.Expected Move.-> OT3
    
    RG4 -.Position Limits.-> OT1
    RG4 -.Stop Loss/Take Profit.-> OT3
    
    OT4 --> Rec
```

## TrendSense → RiskGuard → OptiTrade Pipeline

```mermaid
graph LR
    subgraph "Stage 1: TrendSense"
        direction TB
        I1[Market State Input]
        P1[Calculate Returns]
        P2[Calculate Volatility]
        P3[Moving Averages]
        P4[Probabilistic Model]
        O1[Trend Forecast Output]
        
        I1 --> P1
        I1 --> P2
        I1 --> P3
        P1 --> P4
        P2 --> P4
        P3 --> P4
        P4 --> O1
    end
    
    subgraph "Stage 2: RiskGuard"
        direction TB
        I2[Trend Forecast + Profile]
        C1[Max Risk Constraint]
        C2[Leverage Constraint]
        C3[Risk/Reward Constraint]
        C4[Capital Constraint]
        S1[CSP Solver]
        O2[Risk Parameters Output]
        
        I2 --> C1
        I2 --> C2
        I2 --> C3
        I2 --> C4
        C1 --> S1
        C2 --> S1
        C3 --> S1
        C4 --> S1
        S1 --> O2
    end
    
    subgraph "Stage 3: OptiTrade"
        direction TB
        I3[Forecast + Constraints]
        S2[Generate Candidate States]
        S3[Beam Search]
        S4[Heuristic Evaluation]
        S5[Select Best State]
        O3[Trade Recommendation]
        
        I3 --> S2
        S2 --> S3
        S3 --> S4
        S4 --> S5
        S5 --> O3
    end
    
    O1 -->|probability_up<br/>probability_down<br/>confidence<br/>expected_move| I2
    O2 -->|max_position_size<br/>stop_loss<br/>take_profit<br/>leverage| I3
```

## Detailed Component Interactions

### 1. TrendSense (Probabilistic Reasoning)

**Input:**
- Market State (OHLCV data, indicators)
- Historical price data (sliding window)

**Processing:**
- Calculate technical indicators (SMA, volatility, returns)
- Apply probabilistic model (Bayesian inference)
- Compute probability distribution over trends

**Output:**
```python
TrendForecast {
    direction: "bullish" | "bearish" | "neutral"
    confidence: 0.0 - 1.0
    probability_up: 0.0 - 1.0
    probability_down: 0.0 - 1.0
    probability_neutral: 0.0 - 1.0
    expected_move: float
    uncertainty_score: 0.0 - 1.0
}
```

### 2. RiskGuard (Constraint Satisfaction)

**Input:**
- TrendForecast from TrendSense
- Portfolio state (capital, positions)
- Trader profile (conservative/balanced/aggressive)

**Processing:**
- Define CSP variables (position_size, stop_loss, take_profit, leverage)
- Apply constraints based on trader profile
- Solve using backtracking search with domain filtering

**Output:**
```python
RiskConstraints {
    max_position_size: float
    stop_loss: float
    take_profit: float
    leverage: float
    risk_amount: float
    is_valid: boolean
    constraint_violations: list[str]
}
```

### 3. OptiTrade (Search-Based Optimization)

**Input:**
- TrendForecast from TrendSense
- RiskConstraints from RiskGuard
- Market state
- Portfolio state

**Processing:**
- Generate initial search states (BUY/SELL/HOLD)
- Apply beam search to explore candidate strategies
- Evaluate states using heuristic function:
  - Expected profit (from trend probabilities)
  - Risk-reward ratio
  - Trend alignment
  - Confidence score

**Output:**
```python
TradeRecommendation {
    action: "buy" | "sell" | "hold"
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    leverage: float
    expected_profit: float
    risk_reward_ratio: float
    confidence_score: 0.0 - 1.0
    reasoning: str
}
```

## Classical AI Concepts Mapping

| MCP Tool | AI Concept | Implementation |
|----------|-----------|----------------|
| **TrendSense** | Probabilistic Reasoning | Bayesian inference, probability distributions, uncertainty quantification |
| **RiskGuard** | Constraint Satisfaction | CSP variables, domain filtering, backtracking search, constraint propagation |
| **OptiTrade** | Search Algorithms | State space representation, beam search, greedy best-first, heuristic evaluation |

## Data Dependencies

```mermaid
graph TD
    MD[Market Data] --> TS[TrendSense]
    PF[Portfolio] --> RG[RiskGuard]
    TP[Trader Profile] --> RG
    
    TS --> TF[Trend Forecast]
    TF --> RG
    TF --> OT[OptiTrade]
    
    RG --> RC[Risk Constraints]
    RC --> OT
    
    MD --> OT
    PF --> OT
    
    OT --> TR[Trade Recommendation]
```

## Error Handling Flow

```mermaid
flowchart TD
    Start[API Request] --> TS{TrendSense<br/>Success?}
    
    TS -->|Yes| TF[Trend Forecast]
    TS -->|No| E1[Return Error:<br/>Market Analysis Failed]
    
    TF --> RG{RiskGuard<br/>Valid?}
    
    RG -->|Yes| RC[Risk Constraints]
    RG -->|No| E2[Return HOLD:<br/>Constraints Not Satisfied]
    
    RC --> OT{OptiTrade<br/>Found Strategy?}
    
    OT -->|Yes| Rec[Trade Recommendation]
    OT -->|No| E3[Return HOLD:<br/>No Optimal Strategy]
    
    Rec --> Success[Return Response]
    E1 --> End[Error Response]
    E2 --> End
    E3 --> End
    Success --> End
```

## Performance Considerations

### TrendSense
- **Complexity**: O(n) where n = sliding window size
- **Optimization**: Cache indicator calculations
- **Bottleneck**: Historical data processing

### RiskGuard
- **Complexity**: O(d^v) where d = domain size, v = variables
- **Optimization**: Forward checking, arc consistency
- **Bottleneck**: CSP solver with many constraints

### OptiTrade
- **Complexity**: O(b^d) where b = beam width, d = search depth
- **Optimization**: Limit beam width, prune low-scoring states
- **Bottleneck**: State evaluation with complex heuristics

## Scalability Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/HAProxy]
    end
    
    subgraph "API Instances"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance 3]
    end
    
    subgraph "MCP Tools Pool"
        TS1[TrendSense Worker]
        RG1[RiskGuard Worker]
        OT1[OptiTrade Worker]
    end
    
    subgraph "Data Layer"
        Cache[Redis Cache]
        DB[(Market Data DB)]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> TS1
    API2 --> RG1
    API3 --> OT1
    
    TS1 --> Cache
    RG1 --> Cache
    OT1 --> Cache
    
    Cache --> DB
```

## Future Enhancements

1. **Parallel MCP Execution**: Run TrendSense, RiskGuard, OptiTrade concurrently
2. **Caching Layer**: Cache market data and indicator calculations
3. **Real-time Updates**: WebSocket support for live recommendations
4. **Backtesting Engine**: Historical performance validation
5. **Multi-pair Analysis**: Portfolio-level optimization across pairs
6. **Advanced AI**: Deep learning for TrendSense, reinforcement learning for OptiTrade
