from ib_insync import *
import pandas as pd
import numpy as np
from my_module.indicators import Indicators

columns = [
    "time", "open", "high", "low", "close", "volume", 
    "vwap", "std_dev", "vwap_upper", "vwap_lower", 
    "price_extension", "high_of_day", "low_of_day", "volume_ma", 
    "volume_trend", "extended_up", "extended_down", "breakout_up", 
    "breakout_down", "new_high", "new_low", "trend_up", "trend_down", 
    "rsi", "consolidating", "reversal_up", "reversal_down"
]

# global df
df = pd.DataFrame(columns=columns)

# call back functions -> handle real time bars

def on_real_time_bars(bar):
    global df

    new_row = {
        "time": bar.time,
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "close": bar.close,
        "volume": bar.volume,
        "vwap": np.nan,  # VWAP will be calculated later
        "std_dev": np.nan,  # Std Dev will be calculated later
        "vwap_upper": np.nan,
        "vwap_lower": np.nan,
        "price_extension": np.nan,
        "high_of_day": np.nan,
        "low_of_day": np.nan,
        "volume_ma": np.nan,
        "volume_trend": np.nan,
        "extended_up": np.nan,
        "extended_down": np.nan,
        "breakout_up": np.nan,
        "breakout_down": np.nan,
        "new_high": np.nan,
        "new_low": np.nan,
        "trend_up": np.nan,
        "trend_down": np.nan,
        "rsi": np.nan,
        "consolidating": np.nan,
        "reversal_up": np.nan,
        "reversal_down": np.nan
    }

    # Append new data to DataFrame
    df = df.append(new_row, ignore_index=True)

    # Calculate VWAP and Standard Deviation Bands
    df["vwap"] = Indicators.vwap(df)
    df["std_dev"] = Indicators.std_dev(df)
    df["vwap_upper"] = Indicators.vwap_upper(df, df["std_dev"])
    df["vwap_lower"] = Indicators.vwap_lower(df, df["std_dev"])

    # Basic price momentum and trend indicators
    open_price = df.iloc[0]["open"]
    df["high_of_day"] = Indicators.high_of_day(df)
    df["low_of_day"] = Indicators.low_of_day(df)
    df["price_extension"] = Indicators.price_extension(df, open_price)

    # Volume analysis
    df["volume_ma"] = Indicators.volume_ma(df)
    df["volume_trend"] = Indicators.volume_trend(df)

    # Define trending condition
    df["trend_up"] = Indicators.trend_up(df)
    df["trend_down"] = Indicators.trend_down(df)

    check_alerts()


# Apply reversal detection
def calculate_reversal_signals(df):
    # Price action analysis
    if(len(df) < 5):
        return df
    price_window = 5
    df["price_range"] = (
        df["high"].rolling(price_window).max() - df["low"].rolling(price_window).min()
    ) / df["close"]
    df["consolidating"] = df["price_range"] < df["price_range"].rolling(20).mean() * 0.5

    # Volume analysis for reversals
    df["reversal_up"] = (
        df["consolidating"]
        & (df["volume_trend"] > 1)
        & (df["close"] > df["vwap"])
    )

    df["reversal_down"] = (
        df["consolidating"]
        & (df["volume_trend"] > 1)
        & (df["close"] < df["vwap"])
    )

    return df

def check_alerts():
    if(len(df)<1):
        return
    latest = df.iloc[-1]
    print(latest)

    if latest["reversal_up"]:
        print("\nUPWARD REVERSAL ALERT 🔼")
        print(f"Time: {latest['time']}")
        print(f"Price: ${latest['close']:.2f}")

    if latest["reversal_down"]:
        print("\nDOWNWARD REVERSAL ALERT 🔽")
        print(f"Time: {latest['time']}")
        print(f"Price: ${latest['close']:.2f}")

class ReversalAlgo:
    def __init__(self, ib):
        self.ib = ib
        # self.instance = instance
        self.is_running = False
        self.contract = Stock("AAPL", "SMART", "USD")

    def run(self):
        self.ib.reqRealTimeBars(
            contract=self.contract,
            barSize=5,
            whatToShow="TRADES",
            useRTH=False,
            realTimeBars=True,
            callback=on_real_time_bars
        )

        try:
            self.is_running = True
            while self.is_running:
                # self.ib.waitOnUpdate()
                self.ib.sleep(1)
        except KeyboardInterrupt:
            self.is_running = False
            raise
        finally:
            self.is_running = False