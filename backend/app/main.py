"""
ForexFlow Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import trades, market, mcp
from app.core.config import settings

# Initialize FastAPI application
app = FastAPI(
    title="ForexFlow API",
    description="AI-Powered Forex Trading Simulator using MCP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trades.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(mcp.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "ForexFlow API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_tools": {
            "trend_sense": "available",
            "risk_guard": "available",
            "opti_trade": "available"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
