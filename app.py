import os
import sys
from flask import Flask, render_template, request, jsonify

# Make sure the current directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_simulator import TradingSimulator

app = Flask(__name__)

# Store simulator instances per session (in production, use database)
simulators = {}

def get_simulator(session_id):
    """Get or create a simulator for this session"""
    if session_id not in simulators:
        simulators[session_id] = TradingSimulator(starting_balance=10000)
    return simulators[session_id]

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/portfolio/<session_id>', methods=['GET'])
def get_portfolio(session_id):
    """Get user's portfolio"""
    sim = get_simulator(session_id)
    
    portfolio = []
    total_value = sim.balance
    
    for symbol, quantity in sim.portfolio.items():
        if quantity > 0:
            price = sim.get_stock_price(symbol)
            if price:
                value = price * quantity
                total_value += value
                avg_cost = sum(sim.buy_prices[symbol]) / len(sim.buy_prices[symbol])
                profit = (price - avg_cost) * quantity
                profit_pct = (profit / (avg_cost * quantity)) * 100 if avg_cost * quantity > 0 else 0
                
                portfolio.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': round(price, 2),
                    'value': round(value, 2),
                    'avg_cost': round(avg_cost, 2),
                    'profit': round(profit, 2),
                    'profit_pct': round(profit_pct, 2)
                })
    
    return jsonify({
        'cash': round(sim.balance, 2),
        'portfolio': portfolio,
        'total_value': round(total_value, 2),
        'session_id': session_id
    })

@app.route('/api/buy/<session_id>', methods=['POST'])
def buy(session_id):
    """Buy stock"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    quantity = int(data.get('quantity', 0))
    
    if not symbol or quantity <= 0:
        return jsonify({'success': False, 'message': 'Invalid symbol or quantity'}), 400
    
    sim = get_simulator(session_id)
    success = sim.buy_stock(symbol, quantity)
    
    return jsonify({
        'success': success,
        'message': f"✅ Bought {quantity} shares of {symbol}" if success else "❌ Purchase failed",
        'balance': round(sim.balance, 2)
    })

@app.route('/api/sell/<session_id>', methods=['POST'])
def sell(session_id):
    """Sell stock"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    quantity = int(data.get('quantity', 0))
    
    if not symbol or quantity <= 0:
        return jsonify({'success': False, 'message': 'Invalid symbol or quantity'}), 400
    
    sim = get_simulator(session_id)
    success = sim.sell_stock(symbol, quantity)
    
    return jsonify({
        'success': success,
        'message': f"✅ Sold {quantity} shares of {symbol}" if success else "❌ Sale failed",
        'balance': round(sim.balance, 2)
    })

@app.route('/api/performance/<session_id>', methods=['GET'])
def get_performance(session_id):
    """Get performance stats"""
    sim = get_simulator(session_id)
    
    total_value = sim.balance
    for symbol, quantity in sim.portfolio.items():
        if quantity > 0:
            price = sim.get_stock_price(symbol)
            if price:
                total_value += price * quantity
    
    profit = total_value - 10000
    profit_pct = (profit / 10000) * 100
    
    return jsonify({
        'starting_balance': 10000,
        'current_value': round(total_value, 2),
        'profit': round(profit, 2),
        'profit_pct': round(profit_pct, 2),
        'trades': len(sim.transaction_history)
    })

@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """Get current price for a symbol"""
    sim = TradingSimulator()
    price = sim.get_stock_price(symbol.upper())
    
    if price:
        return jsonify({'symbol': symbol.upper(), 'price': round(price, 2)})
    else:
        return jsonify({'error': 'Could not fetch price'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
