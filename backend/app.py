from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from datetime import datetime

# Import backend logic
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import data_loader
import analytics
import query_engine

app = FastAPI(title="Stock Market Weekday Analyzer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stock")
async def get_stock_data_by_weekday(symbol: str, weekday: str):
    """
    Get all historical records for a specific stock and weekday.
    """
    df = data_loader.get_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Stock data not found or invalid symbol.")
        
    weekday_data = query_engine.filter_by_weekday(df, weekday)
    if not weekday_data:
        raise HTTPException(status_code=404, detail=f"No data available for {weekday}.")
        
    return weekday_data

@app.get("/analytics")
async def get_stock_analytics(symbol: str):
    """
    Get performance analytics per weekday for a given stock.
    """
    df = data_loader.get_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Stock data not found or invalid symbol.")
        
    perf_analytics = analytics.calculate_weekday_performance(df)
    best_day = analytics.get_best_trading_day(perf_analytics)
    
    return {
        "symbol": symbol,
        "analytics": perf_analytics,
        "best_day": best_day
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Serve Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
