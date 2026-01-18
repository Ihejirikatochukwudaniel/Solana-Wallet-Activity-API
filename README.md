# Solana Wallet Activity API

A production-ready FastAPI application for tracking and retrieving Solana wallet activity. This API provides endpoints to fetch wallet summaries and transaction history from the Solana blockchain.

## Features

- **Wallet Summary**: Get comprehensive wallet information including balance and transaction count
- **Transaction History**: Retrieve detailed transaction records with status and fees
- **Async Operations**: All external API calls are asynchronous for high performance
- **Comprehensive Error Handling**: Proper error messages and HTTP status codes
- **Input Validation**: Solana address validation using Pydantic models
- **Rate Limiting Awareness**: Built-in support for Solana RPC rate limiting with retries
- **Production-Ready**: Logging, type hints, and comprehensive documentation
- **API Documentation**: Auto-generated Swagger UI and ReDoc documentation

## Project Structure

```
wallet-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration management
│   ├── routers/
│   │   ├── __init__.py
│   │   └── wallet.py           # Wallet API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── solana.py           # Solana RPC client
│   └── models/
│       ├── __init__.py
│       └── schemas.py          # Pydantic models
├── tests/
│   ├── __init__.py
│   └── test_wallet.py          # Test suite
├── requirements.txt             # Python dependencies
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Requirements

- Python 3.8+
- pip or conda
- Access to a Solana RPC endpoint (default: public mainnet)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd wallet-api
```

### 2. Create a Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
# API_TIMEOUT=30
# MAX_RETRIES=3
```

## Running Locally

### Start the Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

```bash
# Root endpoint
curl http://localhost:8000/

# Health status
curl http://localhost:8000/health
```

### 2. Wallet Summary

Get wallet balance, transaction count, and last activity timestamp.

```bash
curl http://localhost:8000/wallet/7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU/summary
```

**Response:**
```json
{
  "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "balance": 1.42,
  "balance_lamports": 1420000000,
  "tx_count": 37,
  "last_active": "2026-01-15T10:22:00Z"
}
```

### 3. Wallet Transactions

Get recent transactions for a wallet with optional limit parameter.

```bash
# Get default 10 most recent transactions
curl http://localhost:8000/wallet/7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU/transactions

# Get 5 most recent transactions
curl http://localhost:8000/wallet/7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU/transactions?limit=5

# Get up to 100 transactions
curl http://localhost:8000/wallet/7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU/transactions?limit=100
```

**Response:**
```json
{
  "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "transactions": [
    {
      "signature": "5wJ8nk9V5vZ2K6y3P4q5R6s7T8u9V0w1X2y3Z4a5B6c7D8e9F0g1H2i3J4k5L",
      "block_time": "2026-01-16T10:22:00Z",
      "slot": 123456789,
      "status": "success",
      "fee": 5000
    }
  ],
  "count": 1
}
```

## API Parameters

### Wallet Address
- **Format**: Base58-encoded string, 32-44 characters
- **Example**: `7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`

### Transaction Limit
- **Range**: 1-1000
- **Default**: 10
- **Parameter**: `limit` (query parameter)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SOLANA_RPC_URL` | `https://api.mainnet-beta.solana.com` | Solana RPC endpoint URL |
| `API_TIMEOUT` | `30` | RPC request timeout in seconds |
| `MAX_RETRIES` | `3` | Number of retries for failed RPC calls |

## Error Handling

The API returns appropriate HTTP status codes and error messages:

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Invalid request (bad address format) |
| 422 | Validation error (invalid parameter) |
| 503 | RPC service unavailable |
| 500 | Internal server error |

**Error Response Format:**
```json
{
  "error": "Error description here"
}
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_wallet.py
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

### Test Suite Contents

- **Health Check Tests**: Verify root and health endpoints
- **Wallet Summary Tests**: Test address validation and response format
- **Transactions Tests**: Test transaction endpoint and limit validation
- **Model Tests**: Test Pydantic model validation
- **Response Model Tests**: Verify response schemas

## Deployment Instructions

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t solana-wallet-api .
docker run -p 8000:8000 --env-file .env solana-wallet-api
```

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using a Process Manager (e.g., systemd)

Create `/etc/systemd/system/solana-wallet-api.service`:

```ini
[Unit]
Description=Solana Wallet Activity API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/solana-wallet-api
ExecStart=/opt/solana-wallet-api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable solana-wallet-api
sudo systemctl start solana-wallet-api
```

### Environment Configuration for Production

1. Set `SOLANA_RPC_URL` to a reliable RPC endpoint (consider using a paid service)
2. Adjust `API_TIMEOUT` based on your network conditions
3. Enable HTTPS/SSL with a reverse proxy (nginx, Caddy)
4. Implement rate limiting at the API gateway level
5. Set up monitoring and logging aggregation
6. Configure CORS appropriately (restrict origins)

## Performance Considerations

### Caching Opportunities

The codebase includes TODO comments where caching would improve performance:

- **Wallet Summary**: Transaction count is immutable (cacheable with TTL)
- **Transaction History**: Block times don't change (cacheable indefinitely)
- Popular addresses could benefit from response caching

Implementation suggestion:
```python
# Use Redis for distributed caching
# Or implement in-memory cache with TTL using cachetools library
```

### Rate Limiting

The Solana RPC has rate limits. The API includes:

- Automatic retry logic with exponential backoff
- Configurable timeout and retry settings
- Error handling for rate limit responses

For production with high traffic:

- Implement request batching
- Use connection pooling
- Consider a Solana RPC service with higher limits
- Add API gateway rate limiting

## Troubleshooting

### Common Issues

**1. RPC Connection Timeout**
- Check your internet connection
- Verify `SOLANA_RPC_URL` is correct and reachable
- Increase `API_TIMEOUT` if network is slow

**2. Invalid Address Error**
- Ensure the address is a valid Solana address (32-44 base58 characters)
- Check for typos in the address

**3. Rate Limit Errors**
- The API will retry automatically
- If errors persist, consider using a paid RPC service
- Implement request caching to reduce API calls

**4. Wallet Has No Transactions**
- The `/transactions` endpoint will return an empty list
- The `/summary` endpoint will show `last_active: null`

## Development

### Code Style

The project follows PEP 8 standards with:
- Type hints throughout
- Comprehensive docstrings
- Clear variable naming
- Proper error handling

### Adding New Endpoints

1. Create a handler function in `app/routers/wallet.py`
2. Add corresponding Pydantic models in `app/models/schemas.py`
3. Add RPC methods to `app/services/solana.py` if needed
4. Add tests in `tests/test_wallet.py`
5. Update this README

### Logging

The application uses Python's standard logging module:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Error message")
```

Logs include:
- RPC method calls
- Errors and retries
- Request processing

## Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **httpx**: Async HTTP client
- **Python-dotenv**: Environment variable management
- **Pytest**: Testing framework

## License

MIT License - See LICENSE file for details

## Support and Contributing

For issues and contributions:

1. Check existing issues
2. Create a detailed issue report
3. Submit pull requests with tests
4. Follow the code style guidelines

## Roadmap

Future improvements:
- [ ] Response caching with Redis
- [ ] WebSocket support for real-time updates
- [ ] Transaction filtering and search
- [ ] Historical data aggregation
- [ ] Analytics endpoints
- [ ] Token holder information
- [ ] Multi-wallet portfolio tracking

## Performance Benchmarks

Expected performance on mainnet:
- Wallet Summary: ~500-1000ms (depends on RPC)
- Transaction List (10 items): ~2-3s (multiple RPC calls)
- Health Check: <10ms

---

**Last Updated**: January 2026
**API Version**: 1.0.0
