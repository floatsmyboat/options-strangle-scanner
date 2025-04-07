document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const scanButton = document.getElementById('scanButton');
    const scanStatus = document.getElementById('scanStatus');
    const resultsTable = document.getElementById('resultsTable');
    const symbolsInput = document.getElementById('symbolsInput');
    const orderTypeSelect = document.getElementById('orderType');
    const limitPriceGroup = document.getElementById('limitPriceGroup');
    const executeTradeBtn = document.getElementById('executeTradeBtn');
    
    // Current selected trade data
    let selectedTrade = null;
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Order type change handler
    orderTypeSelect.addEventListener('change', function() {
        if (this.value === 'limit') {
            limitPriceGroup.style.display = 'block';
        } else {
            limitPriceGroup.style.display = 'none';
        }
    });
    
    // Scan button click handler
    scanButton.addEventListener('click', function() {
        // Update status
        scanStatus.textContent = 'Scanning...';
        scanStatus.className = 'badge bg-warning';
        scanButton.disabled = true;
        
        // Get symbols
        const symbols = symbolsInput.value.split(',').map(s => s.trim()).filter(s => s);
        
        // Get parameters
        const params = {
            min_price: parseFloat(document.getElementById('minPrice').value),
            max_price: parseFloat(document.getElementById('maxPrice').value),
            min_iv: parseFloat(document.getElementById('minIv').value),
            min_volume: parseInt(document.getElementById('minVolume').value),
            min_open_interest: parseInt(document.getElementById('minOi').value),
            max_dte: parseInt(document.getElementById('maxDte').value),
            min_dte: parseInt(document.getElementById('minDte').value),
            min_delta: parseFloat(document.getElementById('minDelta').value),
            max_delta: parseFloat(document.getElementById('maxDelta').value),
            min_strangle_cost: parseFloat(document.getElementById('minStrangleCost').value),
            max_strangle_cost: parseFloat(document.getElementById('maxStrangleCost').value),
            min_underlying_price: parseFloat(document.getElementById('minUnderlyingPrice').value),
            max_underlying_price: parseFloat(document.getElementById('maxUnderlyingPrice').value),
        };
        
        // Make API request
        fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbols, params }),
        })
        .then(response => response.json())
        .then(data => {
            // Update status
            scanStatus.textContent = `Found ${data.length} results`;
            scanStatus.className = 'badge bg-success';
            
            // Update table
            updateResultsTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
            scanStatus.textContent = 'Error';
            scanStatus.className = 'badge bg-danger';
        })
        .finally(() => {
            scanButton.disabled = false;
        });
    });
    
    // Update results table
    function updateResultsTable(data) {
        const tbody = resultsTable.querySelector('tbody');
        tbody.innerHTML = '';
        
        if (data.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="11" class="text-center">No results found</td>';
            tbody.appendChild(row);
            return;
        }
        
        data.forEach(item => {
            const row = document.createElement('tr');
            
            // Format numbers
            const formatCurrency = num => '$' + num.toFixed(2);
            const formatPercent = num => num.toFixed(2) + '%';
            
            row.innerHTML = `
                <td>${item.symbol}</td>
                <td>${item.expiration}</td>
                <td>${item.dte}</td>
                <td>${item.call_strike.toFixed(2)}</td>
                <td>${item.put_strike.toFixed(2)}</td>
                <td>${formatPercent(item.width_percent)}</td>
                <td>${formatCurrency(item.strangle_cost)}</td>
                <td>${formatPercent(item.avg_iv)}</td>
                <td class="${item.upper_breakeven_pct > 10 ? 'positive' : ''}">${formatPercent(item.upper_breakeven_pct)}</td>
                <td class="${item.lower_breakeven_pct > 10 ? 'positive' : ''}">${formatPercent(item.lower_breakeven_pct)}</td>
                <td>
                    <button class="btn btn-sm btn-primary view-chart" data-symbol="${item.symbol}">
                        <i class="bi bi-graph-up"></i>
                    </button>
                    <button class="btn btn-sm btn-warning trade-btn" data-bs-toggle="modal" data-bs-target="#tradeModal">
                        <i class="bi bi-currency-dollar"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
            
            // Store the data in the row for reference
            row.dataset.item = JSON.stringify(item);
        });
        
        // Add event listeners to buttons
        document.querySelectorAll('.view-chart').forEach(button => {
            button.addEventListener('click', function() {
                const symbol = this.getAttribute('data-symbol');
                loadChart(symbol);
                
                // Highlight the selected row
                document.querySelectorAll('#resultsTable tbody tr').forEach(row => {
                    row.classList.remove('highlight-row');
                });
                this.closest('tr').classList.add('highlight-row');
            });
        });
        
        document.querySelectorAll('.trade-btn').forEach(button => {
            button.addEventListener('click', function() {
                const row = this.closest('tr');
                const item = JSON.parse(row.dataset.item);
                selectedTrade = item;
                
                // Populate trade details
                const tradeDetails = document.getElementById('tradeDetails');
                tradeDetails.innerHTML = `
                    <tr><td>Symbol:</td><td><strong>${item.symbol}</strong></td></tr>
                    <tr><td>Strategy:</td><td>Strangle</td></tr>
                    <tr><td>Expiration:</td><td>${item.expiration} (${item.dte} days)</td></tr>
                    <tr><td>Call Leg:</td><td>${item.call_strike} Strike @ ${item.call_price.toFixed(2)}</td></tr>
                    <tr><td>Put Leg:</td><td>${item.put_strike} Strike @ ${item.put_price.toFixed(2)}</td></tr>
                    <tr><td>Total Cost:</td><td>$${item.strangle_cost.toFixed(2)} per share</td></tr>
                    <tr><td>Implied Volatility:</td><td>${item.avg_iv.toFixed(2)}%</td></tr>
                    <tr><td>Breakeven Points:</td><td>Above ${item.upper_breakeven.toFixed(2)} or Below ${item.lower_breakeven.toFixed(2)}</td></tr>
                `;
                
                // Set default limit price if applicable
                document.getElementById('limitPrice').value = item.strangle_cost.toFixed(2);
            });
        });
    }
    
    // Load chart for a symbol
    function loadChart(symbol) {
        fetch('/api/chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Chart error:', data.error);
                return;
            }
            
            const chartData = JSON.parse(data.chart);
            Plotly.newPlot('priceChart', chartData.data, chartData.layout);
        })
        .catch(error => {
            console.error('Error loading chart:', error);
        });
    }
    
    // Execute trade button handler
    executeTradeBtn.addEventListener('click', function() {
        if (!selectedTrade) return;
        
        const quantity = parseInt(document.getElementById('quantity').value);
        const orderType = document.getElementById('orderType').value;
        const timeInForce = document.getElementById('timeInForce').value;
        
        let tradeRequest = {
            symbol: selectedTrade.symbol,
            strategy: 'strangle',
            quantity: quantity,
            order_type: orderType,
            time_in_force: timeInForce,
            legs: [
                {
                    option_type: 'call',
                    strike: selectedTrade.call_strike,
                    expiration: selectedTrade.expiration,
                    side: 'buy',
                    price: selectedTrade.call_price
                },
                {
                    option_type: 'put',
                    strike: selectedTrade.put_strike,
                    expiration: selectedTrade.expiration,
                    side: 'buy',
                    price: selectedTrade.put_price
                }
            ]
        };
        
        if (orderType === 'limit') {
            tradeRequest.limit_price = parseFloat(document.getElementById('limitPrice').value);
        }
        
        // Execute the trade
        fetch('/api/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tradeRequest),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Trade executed successfully! Order ID: ' + data.order_id);
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('tradeModal'));
                modal.hide();
            } else {
                alert('Trade failed: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error executing trade:', error);
            alert('Error executing trade. See console for details.');
        });
    });
});