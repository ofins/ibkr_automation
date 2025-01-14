import datetime as dt
import time

import matplotlib.pyplot as plt
import pandas as pd
from ib_insync import *
from matplotlib.animation import FuncAnimation


def format_price(price):
    """Format price to 2 decimal places"""
    return f"${price:.2f}"


def format_volume(volume):
    """Format volume with comma separators"""
    return f"{volume:,}"


class SalesHistogram:
    def __init__(self):
        self.ib = IB()
        self.price_buckets = {}  # Store price: count
        self.total_trades = 0

        # Set up the plot
        plt.style.use("default")
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_title("Trade Price Distribution")
        self.ax.set_xlabel("Price")
        self.ax.set_ylabel("Number of Trades")

    def connect(self):
        """Connect to TWS/IBGateway"""
        try:
            self.ib.connect("127.0.0.1", 7497, clientId=1)
            print("Connected to IBKR")
        except Exception as e:
            print(f"Connection error: {e}")

    def start_stream(self, symbol, exchange="SMART", currency="USD"):
        """Start streaming time & sales data"""
        self.symbol = symbol
        contract = Stock(symbol, exchange, currency)
        self.ib.qualifyContracts(contract)

        # Request time & sales data
        self.ib.reqMktData(contract, "233", False, False, [])

        # Set up callback for market data
        self.ib.pendingTickersEvent += self.process_ticks
        print(f"Started streaming for {symbol}")

        # Start the animation
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=1000)
        plt.show()

    def process_ticks(self, tickers):
        """Process ticks from market data"""
        for ticker in tickers:
            if ticker.last > 0:  # Only process valid last trade prices
                price = round(ticker.last, 2)
                # Update price bucket
                self.price_buckets[price] = self.price_buckets.get(price, 0) + 1
                self.total_trades += 1

    def update_plot(self, frame):
        """Update the matplotlib plot"""
        self.ax.clear()

        if not self.price_buckets:  # Skip if no data yet
            return

        # Prepare data for plotting
        prices = list(self.price_buckets.keys())
        counts = list(self.price_buckets.values())

        # Create the bar plot
        bars = self.ax.bar(prices, counts, width=0.02, alpha=0.6)

        # Customize the plot
        self.ax.set_title(
            f"{self.symbol} Trade Price Distribution\nTotal Trades: {format_volume(self.total_trades)}"
        )
        self.ax.set_xlabel("Price ($)")
        self.ax.set_ylabel("Number of Trades")

        # Format price labels
        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:.2f}"))

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        # Add grid
        self.ax.grid(True, alpha=0.3)

        # Adjust layout to prevent label cutoff
        plt.tight_layout()


def main():
    histogram = SalesHistogram()
    histogram.connect()

    # Replace with your desired symbol
    histogram.start_stream("AAPL")

    # The script will keep running due to plt.show()
    try:
        while True:
            histogram.ib.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        histogram.ib.disconnect()
        plt.close()


if __name__ == "__main__":
    main()
