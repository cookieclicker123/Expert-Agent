from typing import List, Dict
import requests
from utils.config import Config
from datetime import datetime, timedelta

class SerperTool:
    def __init__(self):
        self.api_key = Config.api_config.serper_api_key
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
            
        self.base_url = "https://google.serper.dev/search"
        self._cache = {}
        self._cache_expiry = {}
        self.cache_duration = timedelta(minutes=30)
        
        # Trusted financial domains
        self.trusted_domains = [
            'reuters.com',
            'bloomberg.com',
            'finance.yahoo.com',
            'marketwatch.com',
            'fool.com',
            'cnbc.com',
            'wsj.com',
            'ft.com',
            'seekingalpha.com',
            'investing.com'
        ]
        
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Perform search with caching and result processing"""
        cache_key = f"{query}_{num_results}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': num_results * 2  # Request extra to filter
        }
        
        try:
            response = requests.post(
                self.base_url, 
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            results = response.json().get('organic', [])
            
            # Process and filter results
            processed_results = []
            for result in results:
                # Check domain trustworthiness
                if not any(domain in result['link'].lower() 
                          for domain in self.trusted_domains):
                    continue
                    
                processed_results.append({
                    'title': result['title'],
                    'snippet': result['snippet'],
                    'link': result['link'],
                    'date': self._extract_date(result)
                })
                
                if len(processed_results) >= num_results:
                    break
            
            # Cache results
            self._cache[cache_key] = processed_results
            self._cache_expiry[cache_key] = datetime.now() + self.cache_duration
            
            return processed_results
            
        except Exception as e:
            raise Exception(f"Error fetching search results: {str(e)}")
            
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key in self._cache and key in self._cache_expiry:
            return datetime.now() < self._cache_expiry[key]
        return False
        
    def _extract_date(self, result: Dict) -> str:
        """Extract and format date from result"""
        # Try to get date from result metadata
        if 'date' in result:
            return result['date']
            
        # Default to current date if not found
        return datetime.now().strftime("%Y-%m-%d") 