import pandas as pd

def calculate_weekday_performance(df: pd.DataFrame):
    """
    Calculate performance metrics for each weekday.
    """
    if df is None or df.empty:
        return {}
    
    # Calculate group performance
    analytics = {}
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for day in weekdays:
        day_df = df[df['weekday'] == day]
        if day_df.empty:
            continue
            
        def safe_float(val):
            import math
            if math.isnan(val) or math.isinf(val):
                return 0.0
            return float(val)

        metrics = {
            "avg_return": safe_float(day_df['return_percent'].mean() if not day_df.empty else 0),
            "highest_gain": safe_float(day_df['return_percent'].max() if not day_df.empty else 0),
            "highest_loss": safe_float(day_df['return_percent'].min() if not day_df.empty else 0),
            "volatility": safe_float(day_df['return_percent'].std() if len(day_df) > 1 else 0),
            "win_rate": safe_float((day_df['return_percent'] > 0).mean() * 100 if not day_df.empty else 0),
            "count": int(day_df.shape[0])
        }
        analytics[day] = metrics
        
    return analytics

def get_best_trading_day(analytics: dict):
    if not analytics:
        return None
    return max(analytics, key=lambda d: analytics[d]['avg_return'])
