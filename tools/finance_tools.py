from utils.config import Config
from datetime import datetime, timedelta
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class VantageFinanceTool:
    def __init__(self):
        self.api_key = Config.api_config.alpha_vantage_key
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment variables")
        
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5)
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self._cache = {}
        self._cache_expiry = {}
        self.cache_duration = timedelta(minutes=15)  # Cache data for 15 minutes

    def _get_cached_data(self, symbol: str):
        """Get cached data if available and not expired"""
        now = datetime.now()
        if symbol in self._cache and symbol in self._cache_expiry:
            if now < self._cache_expiry[symbol]:
                return self._cache[symbol]
        return None

    def _set_cached_data(self, symbol: str, data: dict):
        """Cache data with expiration"""
        self._cache[symbol] = data
        self._cache_expiry[symbol] = datetime.now() + self.cache_duration

    def get_stock_data(self, symbol: str):
        """Get stock data with caching"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol)
            if cached_data:
                return cached_data

            # Make API calls if not cached
            quote_params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            quote_response = self.session.get(
                self.base_url,
                params=quote_params,
                timeout=10
            )
            quote_data = quote_response.json()
            
            # Check for API limit message
            if "Information" in quote_data and "API rate limit" in quote_data["Information"]:
                raise Exception("Alpha Vantage API rate limit reached. Please try again later or upgrade to a premium plan.")
            
            if "Global Quote" not in quote_data:
                raise Exception(f"Invalid quote response for {symbol}: {quote_data}")
            
            overview_params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": self.api_key
            }
            overview_response = self.session.get(
                self.base_url,
                params=overview_params,
                timeout=10
            )
            overview_data = overview_response.json()
            
            if "Information" in overview_data and "API rate limit" in overview_data["Information"]:
                raise Exception("Alpha Vantage API rate limit reached. Please try again later or upgrade to a premium plan.")

            result = {
                "current_price": {
                    "price": float(quote_data["Global Quote"]["05. price"]),
                    "change_percent": float(quote_data["Global Quote"]["10. change percent"].rstrip('%')),
                    "volume": int(quote_data["Global Quote"]["06. volume"]),
                    "trading_day": quote_data["Global Quote"]["07. latest trading day"]
                },
                "fundamentals": {
                    "market_cap": overview_data.get("MarketCapitalization"),
                    "pe_ratio": overview_data.get("PERatio"),
                    "eps": overview_data.get("EPS")
                }
            }
            
            # Cache the successful result
            self._set_cached_data(symbol, result)
            return result
            
        except Exception as e:
            raise Exception(f"Error fetching stock data for {symbol}: {str(e)}")

    def test_connection(self):
        """Test API connectivity"""
        try:
            response = self.session.get(
                self.base_url,
                params={"function": "TIME_SERIES_INTRADAY", "symbol": "IBM", "interval": "1min", "apikey": self.api_key},
                timeout=5
            )
            return response
        except Exception as e:
            raise Exception(f"API Connection Error: {str(e)}")