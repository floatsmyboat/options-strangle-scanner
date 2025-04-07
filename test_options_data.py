import yfinance as yf
import pandas as pd
from datetime import datetime

def test_options_data(symbol):
    """Test retrieving options data for a given symbol."""
    print(f"\n=== Testing options data for {symbol} ===")
    
    try:
        # Get stock data
        stock = yf.Ticker(symbol)
        current_price = stock.info.get('regularMarketPrice', 0)
        print(f"Current price: ${current_price:.2f}")
        
        # Get options expiration dates
        expirations = stock.options
        print(f"Available expiration dates: {expirations}")
        
        if not expirations:
            print(f"No options data available for {symbol}")
            return
        
        # Get options chain for the first expiration
        exp_date = expirations[0]
        print(f"\nTesting expiration date: {exp_date}")
        
        opt_chain = stock.option_chain(exp_date)
        
        # Check calls
        calls_df = opt_chain.calls
        print(f"\nCall options columns: {calls_df.columns.tolist()}")
        
        if not calls_df.empty:
            print(f"Number of call options: {len(calls_df)}")
            print("\nSample call option:")
            print(calls_df.iloc[0].to_dict())
        else:
            print("No call options found")
        
        # Check puts
        puts_df = opt_chain.puts
        print(f"\nPut options columns: {puts_df.columns.tolist()}")
        
        if not puts_df.empty:
            print(f"Number of put options: {len(puts_df)}")
            print("\nSample put option:")
            print(puts_df.iloc[0].to_dict())
        else:
            print("No put options found")
        
    except Exception as e:
        print(f"Error testing {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test a few symbols known to have liquid options
    test_symbols = ['SPY', 'AAPL', 'TSLA', 'QQQ', 'AMZN']
    
    for symbol in test_symbols:
        test_options_data(symbol)