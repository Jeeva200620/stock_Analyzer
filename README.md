# Stock Market Weekday Analyzer

A professional tool to analyze historical stock performance by weekday.

## Features
- **Weekday Data Search**: Filter historical data by Monday, Tuesday, etc.
- **Performance Analytics**: Average returns, win rates, and volatility per weekday.
- **Visual Insights**: Interactive charts showing weekday performance trends.
- **Cached Data**: Efficiently stores downloaded data locally via `yfinance`.

## How to Run

### 1. Backend (Already running)
The backend is running at `http://localhost:8000`. 
If you need to restart it:
```bash
cd stock-weekday-analyzer
.\venv\Scripts\python.exe -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### 2. Frontend
Simply open the following file in your web browser:
`frontend/index.html`

## Technical Details
- **Backend**: FastAPI, Pandas, yfinance
- **Frontend**: Vanilla JavaScript, CSS3, Chart.js
- **Environment**: Python Virtual Environment (`venv`)

## Stock Symbols
- **NIFTY50**: `^NSEI`
- **NIFTY BEES**: `NIFTYBEES.NS`
- **Reliance**: `RELIANCE.NS`
- **TCS**: `TCS.NS`
- **Apple**: `AAPL`
- **Tesla**: `TSLA`
