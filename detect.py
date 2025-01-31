import numpy as np
import pandas as pd
from ib_insync import *

# Connect to IBKR TWS API
ib = IB()
ib.connect("127.0.0.1", 7497, clientId=1)

# Define contract (Example: AAPL Stock)
contract = Stock("AAPL", "SMART", "USD")

# Fetch historical data (1-minute bars)
bars = ib.reqHistoricalData(
    contract,
    endDateTime="",
    durationStr="1 D",
    barSizeSetting="3 mins",
    whatToShow="TRADES",
    useRTH=True,
    formatDate=1,
)

# Convert data to DataFrame
df = util.df(bars)

# Calculate VWAP and Standard Deviation Bands
df["vwap"] = (
    df["close"]
    .expanding()
    .apply(lambda x: np.average(x, weights=df.loc[x.index, "volume"]))
)
df["std_dev"] = df["close"].rolling(25).std()
df["vwap_upper"] = df["vwap"] + df["std_dev"]
df["vwap_lower"] = df["vwap"] - df["std_dev"]

# Basic price momentum and trend indicators
open_price = df.iloc[0]["open"]
df["high_of_day"] = df["close"].cummax()
df["low_of_day"] = df["close"].cummin()
df["price_extension"] = (df["close"] - open_price) / open_price

# Volume analysis
df["volume_ma"] = df["volume"].rolling(20).mean()
df["volume_trend"] = df["volume"] / df["volume_ma"]

# Trend Detection
df["extended_up"] = df["price_extension"] > 0.01  # 1% up extension
df["extended_down"] = df["price_extension"] < -0.01  # 1% down extension
df["breakout_up"] = df["close"] > df["vwap_upper"]
df["breakout_down"] = df["close"] < df["vwap_lower"]
df["new_high"] = df["close"] > df["high_of_day"].shift(1)
df["new_low"] = df["close"] < df["low_of_day"].shift(1)

# Define trending conditions
df["trend_up"] = (
    df["extended_up"]
    & df["breakout_up"]
    # & (df["volume_trend"] > 1)  # Above average volume
)

df["trend_down"] = (
    df["new_low"]
    & df["extended_down"]
    & df["breakout_down"]
    & (df["volume_trend"] > 1)  # Above average volume
)


# Enhanced Reversal Detection
def calculate_reversal_signals(df):
    # Price action analysis
    price_window = 5
    df["price_range"] = (
        df["high"].rolling(price_window).max() - df["low"].rolling(price_window).min()
    ) / df["close"]
    df["consolidating"] = df["price_range"] < df["price_range"].rolling(20).mean() * 0.5

    # Volume analysis for reversals
    df["volume_declining"] = (
        df["volume"].rolling(5).mean() < df["volume"].rolling(10).mean()
    )

    # Momentum analysis
    df["rsi"] = calculate_rsi(df["close"], periods=14)

    # Detect reversal patterns
    df["reversal_up"] = (
        df["trend_down"].shift(1)  # Was trending down
        & df["consolidating"]  # Price consolidation
        & df["volume_declining"]  # Decreasing volume
        & (df["close"] > df["vwap"])  # Price above VWAP
        & (df["rsi"] > 30)  # RSI showing oversold bounce
    )

    df["reversal_down"] = (
        df["trend_up"].shift(1)  # Was trending up
        & df["consolidating"]  # Price consolidation
        & df["volume_declining"]  # Decreasing volume
        & (df["close"] < df["vwap"])  # Price below VWAP
        & (df["rsi"] < 70)  # RSI showing overbought condition
    )

    return df


def calculate_rsi(series, periods=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# Apply reversal detection
df = calculate_reversal_signals(df)


# Alert function
def check_alerts():
    latest = df.iloc[-1]
    print(latest)

    if latest["reversal_up"]:
        print("\nUPWARD REVERSAL ALERT 🔼")
        print(f"Time: {latest['date']}")
        print(f"Price: ${latest['close']:.2f}")
        print(f"Volume: {latest['volume_trend']:.2f}x average")
        print(f"RSI: {latest['rsi']:.1f}")

    if latest["reversal_down"]:
        print("\nDOWNWARD REVERSAL ALERT 🔽")
        print(f"Time: {latest['date']}")
        print(f"Price: ${latest['close']:.2f}")
        print(f"Volume: {latest['volume_trend']:.2f}x average")
        print(f"RSI: {latest['rsi']:.1f}")


# Run alert check
check_alerts()

# Disconnect from IBKR
ib.disconnect()
