import requests
from datetime import datetime

class TradingSimulator:
    """A simple trading simulator for learning how trading works"""
    
    def __init__(self, starting_balance=10000):
        self.balance = starting_balance
        self.portfolio = {}  # {symbol: quantity}
        self.buy_prices = {}  # Track what price you bought at
        self.transaction_history = []
        
    def get_stock_price(self, symbol):
        """Fetch current stock price using free API"""
        try:
            # Using Alpha Vantage free API
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=demo"
            response = requests.get(url)
            data = response.json()
            
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                price = float(data['Global Quote']['05. price'])
                return price
            else:
                print(f"Could not fetch price for {symbol}. Try another symbol.")
                return None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def buy_stock(self, symbol, quantity):
        """Buy stocks with your virtual money"""
        price = self.get_stock_price(symbol)
        
        if price is None:
            return False
        
        total_cost = price * quantity
        
        if total_cost > self.balance:
            print(f"❌ Not enough money! Need ${total_cost:.2f}, but you only have ${self.balance:.2f}")
            return False
        
        # Add to portfolio
        if symbol not in self.portfolio:
            self.portfolio[symbol] = 0
            self.buy_prices[symbol] = []
        
        self.portfolio[symbol] += quantity
        self.buy_prices[symbol].extend([price] * quantity)
        self.balance -= total_cost
        
        self.transaction_history.append({
            'type': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'date': datetime.now()
        })
        
        print(f"✅ Bought {quantity} shares of {symbol} at ${price:.2f} each")
        print(f"   Balance remaining: ${self.balance:.2f}")
        return True
    
    def sell_stock(self, symbol, quantity):
        """Sell stocks from your portfolio"""
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            print(f"❌ You don't have {quantity} shares of {symbol}")
            return False
        
        price = self.get_stock_price(symbol)
        
        if price is None:
            return False
        
        total_revenue = price * quantity
        self.portfolio[symbol] -= quantity
        self.balance += total_revenue
        
        # Remove from buy prices
        self.buy_prices[symbol] = self.buy_prices[symbol][quantity:]
        
        self.transaction_history.append({
            'type': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_revenue,
            'date': datetime.now()
        })
        
        print(f"✅ Sold {quantity} shares of {symbol} at ${price:.2f} each")
        print(f"   Balance: ${self.balance:.2f}")
        return True
    
    def get_portfolio(self):
        """See what stocks you own"""
        if not self.portfolio:
            print("Your portfolio is empty!")
            return
        
        print("\n📊 YOUR PORTFOLIO:")
        print("-" * 50)
        total_value = self.balance
        
        for symbol, quantity in self.portfolio.items():
            if quantity > 0:
                price = self.get_stock_price(symbol)
                if price:
                    value = price * quantity
                    total_value += value
                    avg_cost = sum(self.buy_prices[symbol]) / len(self.buy_prices[symbol])
                    profit = (price - avg_cost) * quantity
                    print(f"{symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f} (Profit: ${profit:.2f})")
        
        print("-" * 50)
        print(f"Cash: ${self.balance:.2f}")
        print(f"Total Portfolio Value: ${total_value:.2f}")
    
    def get_performance(self):
        """See how much you've made or lost"""
        total_bought = sum([t['total'] for t in self.transaction_history if t['type'] == 'BUY'])
        total_sold = sum([t['total'] for t in self.transaction_history if t['type'] == 'SELL'])
        
        total_value = self.balance
        for symbol, quantity in self.portfolio.items():
            if quantity > 0:
                price = self.get_stock_price(symbol)
                if price:
                    total_value += price * quantity
        
        profit = total_value - 10000  # Starting balance
        
        print(f"\n💰 PERFORMANCE:")
        print(f"Starting Balance: $10,000.00")
        print(f"Current Value: ${total_value:.2f}")
        print(f"Profit/Loss: ${profit:.2f}")
        
        if profit > 0:
            print(f"🎉 You're winning! +{(profit/10000)*100:.2f}%")
        elif profit < 0:
            print(f"📉 You're losing. {(profit/10000)*100:.2f}%")
        else:
            print(f"➖ Break even!")
