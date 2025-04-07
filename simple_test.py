import yfinance as yf
import pandas as pd
from datetime import datetime

def find_strangles(symbol, min_price=0.05, max_price=10.0, min_iv=30):
    """Find potential strangles for a given symbol."""
    print(f"\n=== Finding strangles for {symbol} ===")
    
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
            return []
        
        # Get options chain for the first expiration
        exp_date = expirations[0]
        print(f"\nAnalyzing expiration date: {exp_date}")
        
        opt_chain = stock.option_chain(exp_date)
        
        # Process calls
        calls_df = opt_chain.calls
        
        # Filter calls
        otm_calls = calls_df[
            (calls_df['strike'] > current_price) &  # OTM calls
            (calls_df['lastPrice'] >= min_price) &
            (calls_df['lastPrice'] <= max_price) &
            (calls_df['impliedVolatility'] * 100 >= min_iv)
        ]
        
        print(f"Found {len(otm_calls)} valid OTM calls")
        
        # Process puts
        puts_df = opt_chain.puts
        
        # Filter puts
        otm_puts = puts_df[
            (puts_df['strike'] < current_price) &  # OTM puts
            (puts_df['lastPrice'] >= min_price) &
            (puts_df['lastPrice'] <= max_price) &
            (puts_df['impliedVolatility'] * 100 >= min_iv)
        ]
        
        print(f"Found {len(otm_puts)} valid OTM puts")
        
        # Find potential strangles
        strangles = []
        
        for _, call_row in otm_calls.iterrows():
            for _, put_row in otm_puts.iterrows():
                strangle_cost = call_row['lastPrice'] + put_row['lastPrice']
                
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
                
                strangles.append({
                    'symbol': symbol,
                    'current_price': current_price,
                    'expiration': exp_date,
                    'call_strike': call_strike,
                    'put_strike': put_strike,
                    'call_price': call_row['lastPrice'],
                    'put_price': put_row['lastPrice'],
                    'call_iv': call_row['impliedVolatility'] * 100,
                    'put_iv': put_row['impliedVolatility'] * 100,
                    'avg_iv': avg_iv,
                    'strangle_cost': strangle_cost,
                    'width': width,
                    'width_percent': width_percent,
                    'upper_breakeven': upper_breakeven,
                    'lower_breakeven': lower_breakeven,
                    'upper_breakeven_pct': upper_pct,
                    'lower_breakeven_pct': lower_pct,
                })
        
        print(f"Found {len(strangles)} potential strangles")
        
        # Sort by average IV
        strangles = sorted(strangles, key=lambda x: x['avg_iv'], reverse=True)
        
        # Print top 3 strangles
        if strangles:
            print("\nTop 3 strangles by implied volatility:")
            for i, strangle in enumerate(strangles[:3]):
                print(f"\nStrangle #{i+1}:")
                print(f"  Call: {strangle['call_strike']} strike @ ${strangle['call_price']:.2f} (IV: {strangle['call_iv']:.1f}%)")
                print(f"  Put: {strangle['put_strike']} strike @ ${strangle['put_price']:.2f} (IV: {strangle['put_iv']:.1f}%)")
                print(f"  Total cost: ${strangle['strangle_cost']:.2f}")
                print(f"  Width: {strangle['width']:.1f} points ({strangle['width_percent']:.1f}%)")
                print(f"  Breakevens: ${strangle['lower_breakeven']:.2f} and ${strangle['upper_breakeven']:.2f}")
                print(f"  Avg IV: {strangle['avg_iv']:.1f}%")
        
        return strangles
        
    except Exception as e:
        print(f"Error processing {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    # Test a few symbols known to have liquid options
    test_symbols = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'AMZN']
    
    all_strangles = []
    for symbol in test_symbols:
        strangles = find_strangles(symbol)
        all_strangles.extend(strangles)
    
    print(f"\nTotal strangles found across all symbols: {len(all_strangles)}")