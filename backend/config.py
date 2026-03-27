import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
    
    # Provider preference: "massive", "alphavantage", "yfinance"
    if MASSIVE_API_KEY:
        PRIMARY_PROVIDER = "massive"
    elif ALPHA_VANTAGE_API_KEY and "your_" not in ALPHA_VANTAGE_API_KEY:
        PRIMARY_PROVIDER = "alphavantage"
    else:
        PRIMARY_PROVIDER = "yfinance"

# Ensure data directory exists
if not os.path.exists(Config.DATA_DIR):
    os.makedirs(Config.DATA_DIR)
