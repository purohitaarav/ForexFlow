import logging
from typing import List, Dict, Optional
from app.services.forex_api import ForexAPIService, get_forex_service

logger = logging.getLogger(__name__)

class ForexServiceWrapper:
    """
    Wrapper for ForexAPIService to match the specific function signatures 
    requested in Step 6.5.
    """
    def __init__(self):
        self._service = get_forex_service()

    async def get_quote(self, pair: str) -> Dict:
        """
        Get real-time quote for a single pair.
        """
        return await self._service.fetch_live_quote(pair)

    async def get_quotes(self, pairs: List[str]) -> Dict[str, Dict]:
        """
        Get real-time quotes for multiple pairs.
        """
        return await self._service.fetch_live_quotes(pairs)

    async def convert(self, from_code: str, to_code: str, amount: float) -> Dict:
        """
        Convert currency amount.
        """
        return await self._service.convert_currency(from_code, to_code, amount)

# Singleton instance
_forex_service_wrapper = None

def get_forex_api_service() -> ForexServiceWrapper:
    global _forex_service_wrapper
    if _forex_service_wrapper is None:
        _forex_service_wrapper = ForexServiceWrapper()
    return _forex_service_wrapper
