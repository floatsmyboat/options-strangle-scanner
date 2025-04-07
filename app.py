import os
import json
import pandas as pd
import numpy as np
import yfinance as yf
from flask import Flask, render_template, request, jsonify
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
DEFAULT_SCAN_PARAMS = {
    'min_price': 0.05,           # Minimum option price
    'max_price': 10.0,           # Maximum option price
    'min_iv': 30,                # Minimum implied volatility (%)
    'min_volume': 10,            # Minimum trading volume
    'min_open_interest': 10,     # Minimum open interest
    'max_dte': 60,               # Maximum days to expiration
    'min_dte': 5,                # Minimum days to expiration
    'min_delta': 0.05,           # Minimum delta (absolute value)
    'max_delta': 0.45,           # Maximum delta (absolute value)
    'min_strangle_cost': 0.20,   # Minimum cost of the strangle
    'max_strangle_cost': 15.0,   # Maximum cost of the strangle
    'min_underlying_price': 10,  # Minimum underlying stock price
    'max_underlying_price': 500, # Maximum underlying stock price
}

# List of stocks to scan (can be expanded)
DEFAULT_SYMBOLS = [
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 
    'TSLA', 'NVDA', 'AMD', 'INTC', 'NFLX',
    'SPY', 'QQQ', 'IWM', 'DIA', 'XLF',
    'XLE', 'XLK', 'XLV', 'XLI', 'XLU',
    'COIN', 'GME', 'AMC', 'PLTR', 'SOFI',
    'DIS', 'BA', 'JPM', 'GS', 'MS',
    'XOM', 'CVX', 'PFE', 'JNJ', 'UNH'
]

@app.route('/')
def index():
    return render_template('index.html', default_params=DEFAULT_SCAN_PARAMS, symbols=DEFAULT_SYMBOLS)

@app.route('/api/scan', methods=['POST'])
def scan_options():
    data = request.json
    symbols = data.get('symbols', DEFAULT_SYMBOLS)
    params = data.get('params', DEFAULT_SCAN_PARAMS)
    
    # Limit to 5 symbols for demo purposes to avoid rate limiting
    symbols = symbols[:5]
    
    results = []
    
    for symbol in symbols:
        try:
            print(f"Processing symbol: {symbol}")
            # Get stock data
            stock = yf.Ticker(symbol)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            if current_price < params['min_underlying_price'] or current_price > params['max_underlying_price']:
                print(f"  Skipping {symbol}: Price {current_price} outside range {params['min_underlying_price']}-{params['max_underlying_price']}")
                continue
                
            # Get options expiration dates
            expirations = stock.options
            print(f"  Found {len(expirations)} expiration dates for {symbol}")
            
            for exp_date in expirations:
                # Calculate days to expiration
                exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                dte = (exp_datetime - datetime.now()).days
                
                if dte < params['min_dte'] or dte > params['max_dte']:
                    print(f"  Skipping expiration {exp_date}: DTE {dte} outside range {params['min_dte']}-{params['max_dte']}")
                    continue
                
                print(f"  Processing expiration {exp_date} (DTE: {dte})")
                
                # Get options chain for this expiration
                opt_chain = stock.option_chain(exp_date)
                
                # Process calls
                calls_df = opt_chain.calls
                
                # Filter calls - simplified approach without delta
                otm_calls = calls_df[
                    (calls_df['strike'] > current_price) &  # OTM calls
                    (calls_df['lastPrice'] >= params['min_price']) &
                    (calls_df['lastPrice'] <= params['max_price']) &
                    (calls_df['impliedVolatility'] * 100 >= params['min_iv']) &
                    (calls_df['volume'] >= params['min_volume']) &
                    (calls_df['openInterest'] >= params['min_open_interest'])
                ]
                
                print(f"  Found {len(otm_calls)} valid OTM calls")
                
                # Process puts
                puts_df = opt_chain.puts
                
                # Filter puts - simplified approach without delta
                otm_puts = puts_df[
                    (puts_df['strike'] < current_price) &  # OTM puts
                    (puts_df['lastPrice'] >= params['min_price']) &
                    (puts_df['lastPrice'] <= params['max_price']) &
                    (puts_df['impliedVolatility'] * 100 >= params['min_iv']) &
                    (puts_df['volume'] >= params['min_volume']) &
                    (puts_df['openInterest'] >= params['min_open_interest'])
                ]
                
                print(f"  Found {len(otm_puts)} valid OTM puts")
                
                # Find potential strangles
                strangle_count = 0
                for _, call_row in otm_calls.iterrows():
                    for _, put_row in otm_puts.iterrows():
                        strangle_cost = call_row['lastPrice'] + put_row['lastPrice']
                        
                        if strangle_cost >= params['min_strangle_cost'] and strangle_cost <= params['max_strangle_cost']:
                            # Calculate metrics for the strangle
                            call_strike = call_row['strike']
                            put_strike = put_row['strike']
                            width = call_strike - put_strike
                            width_percent = (width / current_price) * 100
                            
                            # Calculate breakeven points
                            upper_breakeven = call_strike + strangle_cost
                            lower_breakeven = put_strike - strangle_cost
                            
                            # Calculate percent to breakeven
                            upper_pct = ((upper_breakeven / current_price) - 1) * 100
                            lower_pct = (1 - (lower_breakeven / current_price)) * 100
                            
                            # Average IV of the strangle
                            avg_iv = (call_row['impliedVolatility'] + put_row['impliedVolatility']) * 50
                            
                            strangle_count += 1
                            
                            results.append({
                                'symbol': symbol,
                                'current_price': current_price,
                                'expiration': exp_date,
                                'dte': dte,
                                'call_strike': call_strike,
                                'put_strike': put_strike,
                                'call_price': call_row['lastPrice'],
                                'put_price': put_row['lastPrice'],
                                'call_iv': call_row['impliedVolatility'] * 100,
                                'put_iv': put_row['impliedVolatility'] * 100,
                                'avg_iv': avg_iv,
                                'call_volume': call_row['volume'],
                                'put_volume': put_row['volume'],
                                'call_oi': call_row['openInterest'],
                                'put_oi': put_row['openInterest'],
                                'strangle_cost': strangle_cost,
                                'width': width,
                                'width_percent': width_percent,
                                'upper_breakeven': upper_breakeven,
                                'lower_breakeven': lower_breakeven,
                                'upper_breakeven_pct': upper_pct,
                                'lower_breakeven_pct': lower_pct,
                            })
                
                print(f"  Found {strangle_count} valid strangles for {symbol} expiring on {exp_date}")
                
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"Total results found: {len(results)}")
    if len(results) > 0:
        print(f"Sample result: {results[0]}")
    
    # Sort results by average IV (descending)
    results = sorted(results, key=lambda x: x['avg_iv'], reverse=True)
    
    return jsonify(results)

@app.route('/api/chart', methods=['POST'])
def generate_chart():
    data = request.json
    symbol = data.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400
    
    try:
        # Get historical data
        stock = yf.Ticker(symbol)
        hist = stock.history(period='6mo')
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Price'
        )])
        
        # Add volume as bar chart
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name='Volume',
            yaxis='y2',
            marker_color='rgba(0,0,255,0.3)'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Price History',
            yaxis_title='Price',
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right'
            ),
            xaxis_rangeslider_visible=False
        )
        
        # Convert to JSON
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify({'chart': chart_json})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_alpaca_trader():
    """Helper function to get an instance of AlpacaOptionsTrader"""
    # Get API credentials from environment variables
    api_key = os.environ.get('ALPACA_API_KEY')
    api_secret = os.environ.get('ALPACA_API_SECRET')
    
    if api_key and api_secret:
        from trading_integration import AlpacaOptionsTrader
        return AlpacaOptionsTrader(api_key=api_key, api_secret=api_secret)
    return None

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    data = request.json
    
    # Get trader instance
    trader = get_alpaca_trader()
    
    # Check if API credentials are set
    if trader:
        try:
            # Execute the trade
            result = trader.execute_strangle(data)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error executing trade: {str(e)}'
            })
    else:
        # If no API credentials are set, return a mock response
        return jsonify({
            'status': 'success',
            'message': 'Trade simulated successfully (API credentials not set)',
            'trade_details': data,
            'order_id': 'mock-order-' + datetime.now().strftime('%Y%m%d%H%M%S')
        })

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders from Alpaca"""
    trader = get_alpaca_trader()
    
    if trader:
        try:
            # Get orders from Alpaca
            orders = trader.get_orders()
            return jsonify(orders)
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error retrieving orders: {str(e)}'
            })
    else:
        # Return mock data if no API credentials
        return jsonify({
            'status': 'success',
            'orders': [
                {
                    'id': 'mock-order-1',
                    'symbol': 'AAPL',
                    'strategy': 'strangle',
                    'status': 'filled',
                    'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                    'filled_at': datetime.now().isoformat(),
                    'legs': [
                        {'option_type': 'call', 'strike': 180, 'expiration': '2025-04-17'},
                        {'option_type': 'put', 'strike': 160, 'expiration': '2025-04-17'}
                    ],
                    'quantity': 1,
                    'side': 'buy',
                    'type': 'market'
                },
                {
                    'id': 'mock-order-2',
                    'symbol': 'MSFT',
                    'strategy': 'strangle',
                    'status': 'new',
                    'created_at': datetime.now().isoformat(),
                    'legs': [
                        {'option_type': 'call', 'strike': 420, 'expiration': '2025-04-25'},
                        {'option_type': 'put', 'strike': 380, 'expiration': '2025-04-25'}
                    ],
                    'quantity': 2,
                    'side': 'buy',
                    'type': 'limit'
                }
            ]
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=58236, debug=True)