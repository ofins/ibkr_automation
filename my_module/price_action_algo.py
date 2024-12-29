from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz
from ib_insync import Stock


class PriceActionAlgo:
    def __init__(self, ib):
        self.ib = ib
        self.positions = {}
        self.bars_data = {}
        self.threshold = 0.7
        self.lookback = 3

    def get_contract(self, symbol):
        """Create stock contract"""
        contract = Stock(symbol, "SMART", "USD")
        self.ib.qualifyContracts(contract)
        return contract

    def get_historical_data(self, contract, duration="2 D"):
        """Get historical data for initial analysis"""
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting="1 min",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
        )
        return util.df(bars)

    def identify_strong_candles(self, df):
        """Identify strong bullish and bearish candles"""
        df["body_size"] = abs(df["close"] - df["open"])
        df["total_range"] = df["high"] - df["low"]
        df["body_ratio"] = df["body_size"] / df["total_range"]

        df["is_bullish"] = df["close"] > df["open"]
        df["is_bearish"] = df["close"] < df["open"]

        df["is_strong_bullish"] = df["is_bullish"] & (df["body_ratio"] > self.threshold)
        df["is_strong_bearish"] = df["is_bearish"] & (df["body_ratio"] > self.threshold)

        return df

    def check_for_signal(self, df):
        """Generate trading signal based on latest data"""
        df = self.identify_strong_candles(df)
        df["price_change"] = df["close"].pct_change(self.lookback)

        # Get latest candle
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Buy signal
        if (
            latest["price_change"] < 0
            and latest["is_strong_bullish"]
            and not prev["is_strong_bullish"]
        ):
            return 1

        # Sell signal
        elif (
            latest["price_change"] > 0
            and latest["is_strong_bearish"]
            and not prev["is_strong_bearish"]
        ):
            return -1

        return 0

    def on_bar_update(self, bars, has_new_bar):
        """Callback for real-time bar updates"""
        if has_new_bar:
            symbol = bars.contract.symbol
            df = util.df(bars)

            # Update stored data
            self.bars_data[symbol] = df

            # Check for trading signal
            signal = self.check_for_signal(df)

            if signal != 0:
                self.place_order(bars.contract, signal)

    def start_streaming(self, symbol):
        """Start streaming real-time data"""
        contract = self.get_contract(symbol)

        # Get initial historical data
        df = self.get_historical_data(contract)
        self.bars_data[symbol] = df

        # Subscribe to real-time bars
        self.ib.reqRealTimeBars(contract, 5, "TRADES", False)

        # Set callback for bar updates
        self.ib.barUpdateEvent += self.on_bar_update

        print(f"Started streaming for {symbol}")

    def run(self, symbols):
        """Main method to run the trading algo"""
        try:
            for symbol in symbols:
                self.start_streaming(symbol)

            # Keep the program running
            self.ib.run()

        except Exception as e:
            print(f"Error: {str(e)}")
