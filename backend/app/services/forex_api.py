"""
Forex API Service

Provides live forex data fetching with caching and error handling.
Supports multiple forex data providers (Alpha Vantage, Fixer.io, etc.)
"""
import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ForexAPICache:
    """Simple in-memory cache for forex quotes"""
    
    def __init__(self, ttl_seconds: int = 10):
        self.cache: Dict[str, Dict] = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached value if not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires_at']:
                return entry['data']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict):
        """Set cache value with TTL"""
        self.cache[key] = {
            'data': data,
            'expires_at': datetime.now() + timedelta(seconds=self.ttl_seconds)
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()


class ForexAPIService:
    """
    Service for fetching live forex data
    
    Supports:
    - Alpha Vantage (default)
    - Fixer.io
    - ExchangeRate-API
    """
    
    def __init__(self):
        self.base_url = settings.FOREX_API_BASE_URL
        self.api_key = settings.FOREX_API_KEY
        self.cache = ForexAPICache(ttl_seconds=settings.FOREX_CACHE_TTL_SECONDS)
        self.client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=10.0)
        return self.client
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def fetch_live_quote(self, pair: str) -> Dict:
        """
        Fetch live quote for a single forex pair
        
        Args:
            pair: Forex pair (e.g., "EURUSD")
            
        Returns:
            Dictionary with quote data:
            {
                "pair": "EURUSD",
                "timestamp": "2024-01-01T00:00:00Z",
                "bid": 1.1000,
                "ask": 1.1002,
                "spread": 0.0002,
                "price": 1.1001  # Mid price
            }
            
        Raises:
            ValueError: If pair is invalid
            httpx.HTTPError: If API request fails
        """
        # Check cache first
        cache_key = f"quote_{pair}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for {pair}")
            return cached
        
        # Validate pair format
        if not self._validate_pair(pair):
            raise ValueError(f"Invalid forex pair format: {pair}")
        
        # Fetch from API
        try:
            quote_data = await self._fetch_from_api(pair)
            
            # Cache the result
            self.cache.set(cache_key, quote_data)
            
            return quote_data
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching quote for {pair}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching quote for {pair}: {e}")
            raise
    
    async def fetch_live_quotes(self, pairs: List[str]) -> Dict[str, Dict]:
        """
        Fetch live quotes for multiple pairs
        
        Args:
            pairs: List of forex pairs
            
        Returns:
            Dictionary mapping pair to quote data
        """
        results = {}
        
        # Fetch all pairs concurrently
        tasks = [self.fetch_live_quote(pair) for pair in pairs]
        quotes = await asyncio.gather(*tasks, return_exceptions=True)
        
        for pair, quote in zip(pairs, quotes):
            if isinstance(quote, Exception):
                logger.error(f"Error fetching {pair}: {quote}")
                results[pair] = None
            else:
                results[pair] = quote
        
        return results
    
    async def convert_currency(
        self,
        from_code: str,
        to_code: str,
        amount: float
    ) -> Dict:
        """
        Convert currency amount
        
        Args:
            from_code: Source currency code (e.g., "EUR")
            to_code: Target currency code (e.g., "USD")
            amount: Amount to convert
            
        Returns:
            Dictionary with conversion result:
            {
                "from": "EUR",
                "to": "USD",
                "amount": 100.0,
                "result": 110.0,
                "rate": 1.10
            }
        """
        # Construct pair
        pair = f"{from_code}{to_code}"
        
        # Get quote
        quote = await self.fetch_live_quote(pair)
        
        # Use mid price for conversion
        rate = quote['price']
        result = amount * rate
        
        return {
            "from": from_code,
            "to": to_code,
            "amount": amount,
            "result": result,
            "rate": rate,
            "timestamp": quote['timestamp']
        }
    
    async def _fetch_from_api(self, pair: str) -> Dict:
        """
        Fetch quote from configured API provider
        
        Supports Alpha Vantage format by default
        """
        # Determine provider from base URL
        if "alphavantage" in self.base_url.lower():
            return await self._fetch_alpha_vantage(pair)
        elif "fixer" in self.base_url.lower():
            return await self._fetch_fixer(pair)
        elif "exchangerate-api" in self.base_url.lower():
            return await self._fetch_exchangerate_api(pair)
        else:
            # Default to Alpha Vantage format
            return await self._fetch_alpha_vantage(pair)
    
    async def _fetch_alpha_vantage(self, pair: str) -> Dict:
        """
        Fetch from Alpha Vantage API
        
        API: https://www.alphavantage.co/documentation/#fx
        """
        # Split pair into from/to currencies
        from_currency = pair[:3]
        to_currency = pair[3:6]
        
        client = await self._get_client()
        
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "apikey": self.api_key
        }
        
        response = await client.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for error
        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        
        if "Note" in data:
            # Rate limit message
            raise ValueError(f"API Rate Limit: {data['Note']}")
        
        # Parse response
        if "Realtime Currency Exchange Rate" not in data:
            raise ValueError(f"Unexpected API response format: {data}")
        
        rate_data = data["Realtime Currency Exchange Rate"]
        
        # Extract bid/ask (Alpha Vantage provides bid price)
        bid_price = float(rate_data.get("8. Bid Price", rate_data["5. Exchange Rate"]))
        ask_price = float(rate_data.get("9. Ask Price", rate_data["5. Exchange Rate"]))
        
        # If bid/ask not available, estimate from exchange rate
        if bid_price == ask_price:
            mid_price = float(rate_data["5. Exchange Rate"])
            spread = mid_price * 0.0001  # Estimate 1 pip spread
            bid_price = mid_price - spread / 2
            ask_price = mid_price + spread / 2
        
        return {
            "pair": pair,
            "timestamp": rate_data["6. Last Refreshed"],
            "bid": bid_price,
            "ask": ask_price,
            "spread": ask_price - bid_price,
            "price": (bid_price + ask_price) / 2
        }
    
    async def _fetch_fixer(self, pair: str) -> Dict:
        """
        Fetch from Fixer.io API
        
        API: https://fixer.io/documentation
        """
        from_currency = pair[:3]
        to_currency = pair[3:6]
        
        client = await self._get_client()
        
        url = f"{self.base_url}/latest"
        params = {
            "access_key": self.api_key,
            "base": from_currency,
            "symbols": to_currency
        }
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("success"):
            raise ValueError(f"API Error: {data.get('error', {}).get('info', 'Unknown error')}")
        
        rate = data["rates"][to_currency]
        
        # Estimate bid/ask from rate
        spread = rate * 0.0001
        bid_price = rate - spread / 2
        ask_price = rate + spread / 2
        
        return {
            "pair": pair,
            "timestamp": data["date"],
            "bid": bid_price,
            "ask": ask_price,
            "spread": spread,
            "price": rate
        }
    
    async def _fetch_exchangerate_api(self, pair: str) -> Dict:
        """
        Fetch from ExchangeRate-API
        
        API: https://www.exchangerate-api.com/docs/overview
        """
        from_currency = pair[:3]
        to_currency = pair[3:6]
        
        client = await self._get_client()
        
        url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}"
        
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("result") != "success":
            raise ValueError(f"API Error: {data.get('error-type', 'Unknown error')}")
        
        rate = data["conversion_rate"]
        
        # Estimate bid/ask
        spread = rate * 0.0001
        bid_price = rate - spread / 2
        ask_price = rate + spread / 2
        
        return {
            "pair": pair,
            "timestamp": datetime.now().isoformat(),
            "bid": bid_price,
            "ask": ask_price,
            "spread": spread,
            "price": rate
        }
    
    def _validate_pair(self, pair: str) -> bool:
        """Validate forex pair format"""
        if len(pair) != 6:
            return False
        
        # Check if it's in the supported pairs list
        if pair.upper() in settings.FOREX_PAIRS:
            return True
        
        # Allow any 6-character pair (for flexibility)
        return pair.isalpha()


# Global service instance
_forex_service: Optional[ForexAPIService] = None


def get_forex_service() -> ForexAPIService:
    """Get or create forex API service instance"""
    global _forex_service
    if _forex_service is None:
        _forex_service = ForexAPIService()
    return _forex_service


async def close_forex_service():
    """Close forex API service"""
    global _forex_service
    if _forex_service:
        await _forex_service.close()
        _forex_service = None
