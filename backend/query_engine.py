import pandas as pd

def filter_by_weekday(df: pd.DataFrame, weekday: str):
    """
    Filter the dataset for a specific weekday.
    """
    if df is None:
        return []
        
    filtered_df = df[df['weekday'] == weekday]
    
    def safe_float(val):
        import math
        try:
            if math.isnan(val) or math.isinf(val):
                return 0.0
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    # Return Date, Open, High, Low, Close, Volume
    results = []
    for index, row in filtered_df.iterrows():
        results.append({
            "date": str(row['Date'].date()) if hasattr(row['Date'], 'date') else str(row['Date']),
            "open": safe_float(row['Open']),
            "high": safe_float(row['High']),
            "low": safe_float(row['Low']),
            "close": safe_float(row['Close']),
            "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0,
            "return_percent": safe_float(row['return_percent'])
        })
        
    return results
