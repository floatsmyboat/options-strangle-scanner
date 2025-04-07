#!/bin/bash

# Start the server in the background
python app.py > server_log.txt 2>&1 &
SERVER_PID=$!

# Wait for the server to start
sleep 5

# Test the API with curl
curl -X POST \
  http://localhost:58236/api/scan \
  -H 'Content-Type: application/json' \
  -d '{
    "symbols": ["SPY", "QQQ"],
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
}'

# Kill the server
kill $SERVER_PID