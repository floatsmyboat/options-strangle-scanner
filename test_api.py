import requests
import json

def test_scan_api():
    """Test the scan API endpoint."""
    url = "http://localhost:58236/api/scan"
    
    # Use a smaller set of symbols for testing
    payload = {
        "symbols": ["SPY", "QQQ", "AAPL", "TSLA", "AMZN"],
        "params": {
            "min_price": 0.05,
            "max_price": 15.0,
            "min_iv": 20,
            "min_volume": 5,
            "min_open_interest": 5,
            "max_dte": 60,
            "min_dte": 3,
            "min_delta": 0.05,
            "max_delta": 0.45,
            "min_strangle_cost": 0.10,
            "max_strangle_cost": 20.0,
            "min_underlying_price": 10,
            "max_underlying_price": 1000
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        results = response.json()
        print(f"Total results: {len(results)}")
        
        if results:
            print("\nSample result:")
            print(json.dumps(results[0], indent=2))
        else:
            print("No results found")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_scan_api()