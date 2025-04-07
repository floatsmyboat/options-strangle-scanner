# Options Strangle Scanner

A web application for scanning the market for low-priced, highly volatile options that would perform well in a volatile market, based on a strangle trading strategy.

## Features

- **Options Scanner**: Find potential strangle opportunities based on customizable parameters
- **Interactive Charts**: View price history for underlying stocks
- **Trading Integration**: Execute trades directly through the Alpaca API
- **Customizable Parameters**: Fine-tune your scan with various filters

## Market Data Sources

The application currently uses the following data sources:

1. **Yahoo Finance API (yfinance)**: Free options data source with reasonable coverage
   - Pros: Free, easy to use, no API key required
   - Cons: Limited data, potential rate limiting, not suitable for high-frequency use

### Alternative Data Sources

For production use, consider these alternatives:

1. **Polygon.io**: Comprehensive options data with reasonable pricing
   - Pros: High-quality data, good API, historical options data
   - Cons: Paid service (starts at $29/month)

2. **TD Ameritrade API**: Full-featured options data if you have an account
   - Pros: Comprehensive data, real-time quotes, free with TD account
   - Cons: Requires TD Ameritrade account, rate limits

3. **Interactive Brokers API**: Professional-grade options data
   - Pros: Institutional quality, comprehensive coverage
   - Cons: Complex integration, requires IB account

4. **CBOE DataShop**: Direct from the source
   - Pros: Highest quality options data
   - Cons: Expensive, complex integration

## Trading Integration

The application includes integration with the Alpaca API for executing trades:

1. **Alpaca**:
   - Pros: Developer-friendly API, commission-free trading, paper trading available
   - Cons: Limited options support (in development)
   - Documentation: [Alpaca API Docs](https://alpaca.markets/docs/api-documentation/)

### Alternative Trading Providers

1. **TD Ameritrade API**:
   - Pros: Comprehensive options trading support, good documentation
   - Cons: Requires TD account
   - Documentation: [TD Ameritrade API](https://developer.tdameritrade.com/apis)

2. **Interactive Brokers API**:
   - Pros: Professional-grade, comprehensive options support
   - Cons: Complex integration
   - Documentation: [IBKR API](https://www.interactivebrokers.com/en/index.php?f=5041)

3. **TradeStation API**:
   - Pros: Good options support, WebAPI available
   - Cons: Requires TradeStation account
   - Documentation: [TradeStation WebAPI](https://www.tradestation.com/technology/webapi/)

## Recommended Scan Parameters

For finding low-priced, highly volatile options for strangles:

1. **Price Range**: $0.10 - $5.00 per contract
2. **Implied Volatility**: Minimum 50% (higher is better for strangles)
3. **Days to Expiration**: 7-45 days (balances time decay with event capture)
4. **Delta Range**: 0.10 - 0.35 (controls how far OTM the options are)
5. **Volume/Open Interest**: Minimum 100 (ensures liquidity)
6. **Strangle Width**: Look for wider strangles in higher volatility environments

## Installation and Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your API keys (for trading integration):
   ```
   export ALPACA_API_KEY="your_api_key"
   export ALPACA_API_SECRET="your_api_secret"
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Access the web interface at http://localhost:50565

## Usage

1. Configure your scan parameters
2. Enter the symbols you want to scan
3. Click "Scan for Strangles"
4. Review the results in the table
5. Click on a symbol to view its price chart
6. Click the trade button to execute a trade

## Disclaimer

This application is for educational and informational purposes only. Options trading involves significant risk and is not suitable for all investors. Always do your own research and consider consulting with a financial advisor before making investment decisions.