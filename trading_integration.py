import os
import json
import alpaca_trade_api as tradeapi
from datetime import datetime

class AlpacaOptionsTrader:
    """
    Integration with Alpaca API for options trading.
    
    Note: Alpaca requires a brokerage account with options trading enabled.
    This is a demonstration of how the integration would work.
    """
    
    def __init__(self, api_key=None, api_secret=None, base_url=None):
        """
        Initialize the Alpaca API client.
        
        Args:
            api_key (str): Alpaca API key (defaults to environment variable)
            api_secret (str): Alpaca API secret (defaults to environment variable)
            base_url (str): Alpaca API base URL (defaults to paper trading URL)
        """
        self.api_key = api_key or os.environ.get('ALPACA_API_KEY')
        self.api_secret = api_secret or os.environ.get('ALPACA_API_SECRET')
        self.base_url = base_url or 'https://paper-api.alpaca.markets'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Alpaca API credentials are required. Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables.")
        
        self.api = tradeapi.REST(
            self.api_key,
            self.api_secret,
            self.base_url,
            api_version='v2'
        )
    
    def get_account(self):
        """Get account information."""
        return self.api.get_account()
    
    def execute_strangle(self, trade_request):
        """
        Execute a strangle options strategy.
        
        Args:
            trade_request (dict): Trade request with the following structure:
                {
                    "symbol": "AAPL",
                    "strategy": "strangle",
                    "quantity": 1,
                    "order_type": "market" or "limit",
                    "time_in_force": "day", "gtc", "ioc",
                    "limit_price": 1.50,  # Only for limit orders
                    "legs": [
                        {
                            "option_type": "call",
                            "strike": 150.0,
                            "expiration": "2023-06-16",
                            "side": "buy",
                            "price": 0.75
                        },
                        {
                            "option_type": "put",
                            "strike": 140.0,
                            "expiration": "2023-06-16",
                            "side": "buy",
                            "price": 0.65
                        }
                    ]
                }
        
        Returns:
            dict: Order confirmation details
        """
        # Validate the trade request
        self._validate_trade_request(trade_request)
        
        # Create the order legs
        legs = []
        for leg in trade_request['legs']:
            # Format the option symbol in OCC format
            # Example: AAPL230616C00150000 (AAPL, June 16 2023, Call, $150.00 strike)
            expiration_date = datetime.strptime(leg['expiration'], '%Y-%m-%d')
            exp_str = expiration_date.strftime('%y%m%d')
            option_type_code = 'C' if leg['option_type'].lower() == 'call' else 'P'
            strike_str = f"{int(leg['strike'] * 1000):08d}"
            option_symbol = f"{trade_request['symbol']}{exp_str}{option_type_code}{strike_str}"
            
            legs.append({
                'symbol': option_symbol,
                'side': leg['side'].upper(),
                'qty': trade_request['quantity']
            })
        
        # Create the order parameters
        order_params = {
            'legs': legs,
            'type': trade_request['order_type'].upper(),
            'time_in_force': trade_request['time_in_force'].upper()
        }
        
        # Add limit price if applicable
        if trade_request['order_type'].lower() == 'limit' and 'limit_price' in trade_request:
            order_params['limit_price'] = trade_request['limit_price']
        
        try:
            # Submit the order
            # Note: In a real implementation, this would call the Alpaca API
            # order = self.api.submit_order_option_spread(**order_params)
            
            # For demonstration, we'll return a mock response
            order_id = f"mock-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                'status': 'success',
                'order_id': order_id,
                'message': 'Order submitted successfully',
                'order_details': {
                    'symbol': trade_request['symbol'],
                    'strategy': trade_request['strategy'],
                    'quantity': trade_request['quantity'],
                    'order_type': trade_request['order_type'],
                    'time_in_force': trade_request['time_in_force'],
                    'legs': trade_request['legs']
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _validate_trade_request(self, trade_request):
        """Validate the trade request structure."""
        required_fields = ['symbol', 'strategy', 'quantity', 'order_type', 'time_in_force', 'legs']
        for field in required_fields:
            if field not in trade_request:
                raise ValueError(f"Missing required field: {field}")
        
        if trade_request['strategy'].lower() != 'strangle':
            raise ValueError(f"Unsupported strategy: {trade_request['strategy']}")
        
        if len(trade_request['legs']) != 2:
            raise ValueError(f"Strangle strategy requires exactly 2 legs, got {len(trade_request['legs'])}")
        
        # Check if we have one call and one put
        option_types = [leg['option_type'].lower() for leg in trade_request['legs']]
        if 'call' not in option_types or 'put' not in option_types:
            raise ValueError("Strangle strategy requires one call and one put option")
        
        # Check if order type is valid
        valid_order_types = ['market', 'limit']
        if trade_request['order_type'].lower() not in valid_order_types:
            raise ValueError(f"Invalid order type: {trade_request['order_type']}")
        
        # Check if limit price is provided for limit orders
        if trade_request['order_type'].lower() == 'limit' and 'limit_price' not in trade_request:
            raise ValueError("Limit price is required for limit orders")
        
        # Check if time in force is valid
        valid_tif = ['day', 'gtc', 'ioc']
        if trade_request['time_in_force'].lower() not in valid_tif:
            raise ValueError(f"Invalid time in force: {trade_request['time_in_force']}")


# Example usage:
if __name__ == "__main__":
    # This would be set in a real environment
    os.environ['ALPACA_API_KEY'] = 'YOUR_API_KEY'
    os.environ['ALPACA_API_SECRET'] = 'YOUR_API_SECRET'
    
    try:
        trader = AlpacaOptionsTrader()
        
        # Example trade request
        trade_request = {
            "symbol": "AAPL",
            "strategy": "strangle",
            "quantity": 1,
            "order_type": "limit",
            "time_in_force": "day",
            "limit_price": 1.50,
            "legs": [
                {
                    "option_type": "call",
                    "strike": 150.0,
                    "expiration": "2023-06-16",
                    "side": "buy",
                    "price": 0.75
                },
                {
                    "option_type": "put",
                    "strike": 140.0,
                    "expiration": "2023-06-16",
                    "side": "buy",
                    "price": 0.65
                }
            ]
        }
        
        result = trader.execute_strangle(trade_request)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")