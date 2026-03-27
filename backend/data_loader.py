import yfinance as yf
import pandas as pd
import os
import requests
from datetime import datetime
from config import Config

def get_massive_data(symbol: str):
    """
    Fetch stock data from Massive.com (Polygon.io rebranded).
    """
    if not Config.MASSIVE_API_KEY:
        return None
        
    print(f"Downloading data for {symbol} via Massive.com...")
    # Massive uses Polygon's v2/aggs structure
    # Free tier usually has 2 years of history. We'll try to get as much as possible.
    to_date = datetime.now().strftime('%Y-%m-%d')
    # Use a safe 2-year window for free plan
    from_date = (datetime.now().replace(year=datetime.now().year - 2)).strftime('%Y-%m-%d')
    
    url = f"https://api.massive.com/v2/aggs/ticker/{symbol}/range/1/day/{from_date}/{to_date}?adjusted=true&sort=asc&apiKey={Config.MASSIVE_API_KEY}"
    
    try:
        r = requests.get(url)
        data = r.json()
        
        if "results" not in data or not data["results"]:
            print(f"Massive.com error: {data.get('status', 'Unknown status')} - {data.get('error', 'No results found')}")
            return None
            
        # Transform results
        processed_data = []
        for res in data["results"]:
            processed_data.append({
                "Date": datetime.fromtimestamp(res["t"] / 1000.0),
                "Open": res["o"],
                "High": res["h"],
                "Low": res["l"],
                "Close": res["c"],
                "Volume": res["v"]
            })
            
        df = pd.DataFrame(processed_data)
        return df
    except Exception as e:
        print(f"Massive.com error: {str(e)}")
        return None

def get_alphavantage_data(symbol: str):
    """
    Fetch stock data from Alpha Vantage.
    """
    if not Config.ALPHA_VANTAGE_API_KEY or "your_" in Config.ALPHA_VANTAGE_API_KEY:
        return None
        
    print(f"Downloading data for {symbol} via Alpha Vantage...")
    # Alpha Vantage doesn't use suffixes like .NS in the same way, but let's try
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={Config.ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    
    if "Time Series (Daily)" not in data:
        print(f"Alpha Vantage error: {data.get('Note', data.get('Error Message', 'Unknown Error'))}")
        return None
        
    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index')
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    
    # Rename columns to match our standard
    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    }, inplace=True)
    
    return df

def get_stock_data(symbol: str):
    """
    Fetch stock data from preferred source or load from local cache.
    """
    file_path = os.path.join(Config.DATA_DIR, f"{symbol}.csv")
    
    # Check if we have cached data for today
    if os.path.exists(file_path):
        # We read the CSV and perform a quick cleanup in case of header corruption
        df = pd.read_csv(file_path)
        
        # Drop rows where 'Date' might be an artifact of MultiIndex (like containing a Ticker string)
        if not df.empty:
            df = df[df['Date'].astype(str).str.match(r'\d{4}-\d{2}-\d{2}') == True]
            
        # Coerce numeric columns just in case
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=['Open', 'Close', 'Date'], inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    # Download data
    data = None
    if Config.PRIMARY_PROVIDER == "massive":
        data = get_massive_data(symbol)
    elif Config.PRIMARY_PROVIDER == "alphavantage":
        data = get_alphavantage_data(symbol)
    
    if data is None: # Fallback chain
        if Config.MASSIVE_API_KEY and Config.PRIMARY_PROVIDER != "massive":
             data = get_massive_data(symbol)
        
        if data is None and Config.ALPHA_VANTAGE_API_KEY and Config.PRIMARY_PROVIDER != "alphavantage":
            data = get_alphavantage_data(symbol)
            
        if data is None:
            print(f"Downloading data for {symbol} via yfinance...")
            data = yf.download(symbol, start="2000-01-01", end=datetime.now().strftime('%Y-%m-%d'))
    
    if data is None or data.empty:
        return None
    
    # Preprocess
    data.reset_index(inplace=True)
    
    # Handle multi-index columns if necessary (specific to yfinance)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] if col[1] == "" or col[1] == symbol else f"{col[0]}_{col[1]}" for col in data.columns]
    
    # Standardize column names
    col_map = {c: c.capitalize() for c in data.columns if c.lower() in ["date", "open", "high", "low", "close", "volume", "index"]}
    data.rename(columns=col_map, inplace=True)
    
    # If index was renamed to Date, or if Date isn't there, check for Index
    if 'Index' in data.columns and 'Date' not in data.columns:
        data.rename(columns={'Index': 'Date'}, inplace=True)
    
    data['Date'] = pd.to_datetime(data['Date'])
    data['weekday'] = data['Date'].dt.day_name()
    
    # Ensure numeric types
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            
    data['return'] = data['Close'] - data['Open']
    data['return_percent'] = (data['Close'] - data['Open']) / data['Open'] * 100
    
    # Fill NaN to avoid JSON issues later
    data = data.ffill().fillna(0)
    data.to_csv(file_path, index=False)
    
    return data
