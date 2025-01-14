import datetime as dt
import time
from collections import deque

import pandas as pd
from ib_insync import *


def format_price(price):
    """Format price to 2 decimal places"""
    return f"${price:.2f}"


def format_volume(volume):
    """Format volume with comma separators"""
    return f"{volume:,}"


class SalesHistogram:
    def __init__(self, max_trades=1000):
        self.ib = IB()
        self.price_buckets = {}  # Store price: count
        self.total_trades = 0
        self.max_trades = max_trades
        self.trade_queue = deque(maxlen=max_trades)  # Store individual trade prices

    def connect(self):
        """Connect to TWS/IBGateway"""
        try:
            self.ib.connect("127.0.0.1", 7497, clientId=1)
            print("Connected to IBKR")
        except Exception as e:
            print(f"Connection error: {e}")

    def start_stream(self, symbol, exchange="SMART", currency="USD"):
        """Start streaming time & sales data"""
        contract = Stock(symbol, exchange, currency)
        self.ib.qualifyContracts(contract)

        # Request time & sales data
        self.ib.reqMktData(contract, "233", False, False, [])

        # Set up callback for market data
        self.ib.pendingTickersEvent += self.process_ticks
        print(f"Started streaming for {symbol}")

    def update_price_buckets(self):
        """Recalculate price buckets from trade queue"""
        self.price_buckets.clear()
        for price in self.trade_queue:
            self.price_buckets[price] = self.price_buckets.get(price, 0) + 1

    def process_ticks(self, tickers):
        """Process ticks from market data"""
        for ticker in tickers:
            if ticker.last > 0:  # Only process valid last trade prices
                price = round(ticker.last, 2)

                # Add new trade to queue (automatically removes oldest if full)
                self.trade_queue.append(price)

                # Update total trades counter
                self.total_trades += 1

                # Recalculate price buckets
                self.update_price_buckets()

                # Print update every 5 trades
                if self.total_trades % 50 == 0:
                    self.print_histogram()

    def print_histogram(self):
        """Print readable histogram to console"""
        if not self.price_buckets:  # Skip if no data yet
            return

        print("\n" + "=" * 50)
        print(f"Active Trades: {format_volume(len(self.trade_queue))}")
        print(f"Total Trades Seen: {format_volume(self.total_trades)}")
        print("Price Distribution:")
        print("-" * 50)

        # Sort by price
        sorted_prices = sorted(self.price_buckets.items())
        max_count = max(self.price_buckets.values())

        for price, count in sorted_prices:
            bar_length = int((count / max_count) * 30)
            bar = "#" * bar_length
            print(
                f"{format_price(price):>10} | {bar:<30} ({format_volume(count)} trades)"
            )

        print("=" * 50 + "\n")


def main():
    histogram = SalesHistogram(max_trades=1000)
    histogram.connect()

    # Replace with your desired symbol
    histogram.start_stream("AAPL")

    # Keep script running
    try:
        while True:
            histogram.ib.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        histogram.ib.disconnect()


if __name__ == "__main__":
    main()
