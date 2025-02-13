from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper


class TrendAnalyzer(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.vwap_data = []
        self.is_trending_up = False
        self.last_high = float("-inf")
        self.opening_price = None
        self.min_extension = 0.01  # 1% minimum extension from opening price
        self.consolidation_threshold = (
            0.002  # 0.2% price movement threshold for consolidation
        )
        self.consolidation_period = 5  # Number of bars to check for consolidation

    def error(self, reqId, errorCode, errorString):
        print(f"Error {errorCode}: {errorString}")

    def historicalData(self, reqId, bar):
        # Store incoming bar data
        bar_data = {
            "timestamp": datetime.strptime(bar.date, "%Y%m%d %H:%M:%S"),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "vwap": bar.average,
        }
        self.data.append(bar_data)
        self.analyze_trend()

    def analyze_trend(self):
        if len(self.data) < 20:  # Need enough data for analysis
            return

        df = pd.DataFrame(self.data)

        # Set opening price if not set
        if self.opening_price is None:
            self.opening_price = df.iloc[0]["open"]

        current_bar = df.iloc[-1]

        # Calculate VWAP standard deviation
        vwap_std = df["vwap"].std()
        current_vwap = current_bar["vwap"]

        # Check if price has extended from opening price
        price_extension = (
            current_bar["close"] - self.opening_price
        ) / self.opening_price

        # Check if price is above VWAP + 1 standard deviation
        vwap_breakout = current_bar["close"] > (current_vwap + vwap_std)

        # Check for new high
        new_high = current_bar["high"] > self.last_high
        if new_high:
            self.last_high = current_bar["high"]

        # Determine if trending up
        if price_extension > self.min_extension and vwap_breakout and new_high:
            self.is_trending_up = True
            print(f"Uptrend detected at {current_bar['timestamp']}")

            # Check for potential reversal
            self.check_reversal(df)

    def check_reversal(self, df):
        if not self.is_trending_up:
            return

        recent_bars = df.tail(self.consolidation_period)

        # Check for price consolidation
        price_range = (
            recent_bars["high"].max() - recent_bars["low"].min()
        ) / recent_bars["low"].min()

        # Check for decreasing volume
        volume_trend = recent_bars["volume"].pct_change().mean()

        # Check for resistance (multiple touches of similar price level)
        high_prices = recent_bars["high"].values
        resistance_touches = sum(
            1
            for x in high_prices
            if abs(x - max(high_prices)) < self.consolidation_threshold
        )

        if (
            price_range < self.consolidation_threshold
            and volume_trend < 0
            and resistance_touches >= 2
        ):
            print(f"⚠️ Potential reversal detected at {df.iloc[-1]['timestamp']}")
            print(f"Price range: {price_range:.4f}")
            print(f"Volume trend: {volume_trend:.4f}")
            print(f"Resistance touches: {resistance_touches}")
            self.is_trending_up = False


def main():
    # Create and connect the client
    app = TrendAnalyzer()
    app.connect("127.0.0.1", 7497, 0)

    # Define the contract (example for AAPL stock)
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    # Request historical data
    app.reqHistoricalData(
        1,  # reqId
        contract,
        "",  # endDateTime
        "1 D",  # durationStr
        "1 min",  # barSizeSetting
        "TRADES",  # whatToShow
        1,  # useRTH
        1,  # formatDate
        False,  # keepUpToDate
        [],  # chartOptions
    )

    app.run()


if __name__ == "__main__":
    main()

# this is a test