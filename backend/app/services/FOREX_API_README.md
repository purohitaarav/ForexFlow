# Forex API Service

## Overview

The Forex API Service provides live forex data fetching with caching, error handling, and support for multiple data providers.

## Supported Providers

### 1. Alpha Vantage (Default)
- **Website**: https://www.alphavantage.co/
- **Free Tier**: 5 API calls per minute, 500 per day
- **Get API Key**: https://www.alphavantage.co/support/#api-key
- **Documentation**: https://www.alphavantage.co/documentation/#fx

### 2. Fixer.io
- **Website**: https://fixer.io/
- **Free Tier**: 100 requests per month
- **Documentation**: https://fixer.io/documentation

### 3. ExchangeRate-API
- **Website**: https://www.exchangerate-api.com/
- **Free Tier**: 1,500 requests per month
- **Documentation**: https://www.exchangerate-api.com/docs/overview

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Alpha Vantage (default)
FOREX_API_KEY=your_api_key_here
FOREX_API_BASE_URL=https://www.alphavantage.co/query

# Or use Fixer.io
# FOREX_API_KEY=your_fixer_key
# FOREX_API_BASE_URL=http://data.fixer.io/api

# Or use ExchangeRate-API
# FOREX_API_KEY=your_exchangerate_key
# FOREX_API_BASE_URL=https://v6.exchangerate-api.com/v6

# Cache settings
FOREX_CACHE_TTL_SECONDS=10
```

### Getting Started

1. **Get an API key** from one of the providers above
2. **Copy `.env.example` to `.env`**:
   ```bash
   cp .env.example .env
   ```
3. **Update `.env`** with your API key
4. **Restart the backend server**

## Usage

### Fetch Single Quote

```python
from app.services.forex_api import get_forex_service

# Get service instance
forex_service = get_forex_service()

# Fetch live quote
quote = await forex_service.fetch_live_quote("EURUSD")

print(quote)
# {
#     "pair": "EURUSD",
#     "timestamp": "2024-01-01T00:00:00Z",
#     "bid": 1.1000,
#     "ask": 1.1002,
#     "spread": 0.0002,
#     "price": 1.1001
# }
```

### Fetch Multiple Quotes

```python
pairs = ["EURUSD", "GBPUSD", "USDJPY"]
quotes = await forex_service.fetch_live_quotes(pairs)

for pair, quote in quotes.items():
    if quote:
        print(f"{pair}: {quote['price']}")
```

### Currency Conversion

```python
result = await forex_service.convert_currency("EUR", "USD", 100.0)

print(result)
# {
#     "from": "EUR",
#     "to": "USD",
#     "amount": 100.0,
#     "result": 110.0,
#     "rate": 1.10,
#     "timestamp": "2024-01-01T00:00:00Z"
# }
```

## Caching

The service includes an in-memory cache to avoid excessive API calls:

- **TTL**: Configurable (default: 10 seconds)
- **Automatic expiration**: Old entries are automatically removed
- **Per-pair caching**: Each forex pair is cached separately

### Cache Behavior

```python
# First call - fetches from API
quote1 = await forex_service.fetch_live_quote("EURUSD")  # API call

# Second call within TTL - returns cached data
quote2 = await forex_service.fetch_live_quote("EURUSD")  # From cache

# After TTL expires - fetches from API again
await asyncio.sleep(11)  # Wait for cache to expire
quote3 = await forex_service.fetch_live_quote("EURUSD")  # API call
```

## Error Handling

The service handles various error scenarios:

### Invalid Pair

```python
try:
    quote = await forex_service.fetch_live_quote("INVALID")
except ValueError as e:
    print(f"Invalid pair: {e}")
```

### API Rate Limit

```python
try:
    quote = await forex_service.fetch_live_quote("EURUSD")
except ValueError as e:
    if "Rate Limit" in str(e):
        print("API rate limit exceeded")
```

### Network Error

```python
import httpx

try:
    quote = await forex_service.fetch_live_quote("EURUSD")
except httpx.HTTPError as e:
    print(f"Network error: {e}")
```

## Testing

### Test Endpoint

Test the forex API service using the built-in endpoint:

```bash
# Test with default pair (EURUSD)
curl http://localhost:8000/api/market/test_live_quote

# Test with specific pair
curl "http://localhost:8000/api/market/test_live_quote?pair=GBPUSD"
```

### Response Format

```json
{
  "success": true,
  "data": {
    "pair": "EURUSD",
    "timestamp": "2024-01-01 00:00:00",
    "bid": 1.1000,
    "ask": 1.1002,
    "spread": 0.0002,
    "price": 1.1001
  },
  "cached": false
}
```

## Integration with TrendSense

The market service automatically tries to use live data:

```python
from app.services.market_service import MarketService

market_service = MarketService()

# Tries live data first, falls back to mock if unavailable
market_state = await market_service.get_market_state("EURUSD")
```

## Performance

- **Cache Hit**: ~0.1ms
- **Cache Miss (API call)**: ~200-500ms
- **Concurrent Requests**: Supported via asyncio

## Rate Limits

### Alpha Vantage
- **Free**: 5 calls/minute, 500 calls/day
- **Premium**: Higher limits available

### Fixer.io
- **Free**: 100 calls/month
- **Paid**: 1,000+ calls/month

### ExchangeRate-API
- **Free**: 1,500 calls/month
- **Paid**: 100,000+ calls/month

## Best Practices

1. **Use caching**: Set appropriate TTL to balance freshness and API usage
2. **Handle errors**: Always wrap API calls in try-except blocks
3. **Monitor usage**: Track API calls to avoid rate limits
4. **Fallback strategy**: Have mock data as fallback for development
5. **Close client**: Call `await forex_service.close()` on shutdown

## Troubleshooting

### "API Rate Limit" Error

**Solution**: 
- Increase cache TTL
- Upgrade to paid API plan
- Switch to different provider

### "Invalid API Key" Error

**Solution**:
- Check `.env` file has correct API key
- Verify API key is active
- Restart backend server

### "Network Error"

**Solution**:
- Check internet connection
- Verify API base URL is correct
- Check firewall settings

## Future Enhancements

1. **Persistent caching**: Use Redis for distributed caching
2. **Historical data**: Fetch actual historical OHLCV data
3. **WebSocket support**: Real-time streaming quotes
4. **Multiple providers**: Automatic failover between providers
5. **Rate limit handling**: Automatic backoff and retry
