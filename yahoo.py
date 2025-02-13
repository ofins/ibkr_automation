import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define stock symbol
ticker = "AAPL"
df = yf.download(ticker, period="5d", interval="5m")

if df.empty:
    print("No data found for ticker:", ticker)
    exit()

# Calculate VWAP directly
typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
price_volume = typical_price * df["Volume"]
df["VWAP"] = price_volume.cumsum() / df["Volume"].cumsum()

# Calculate standard deviation bands
df["StdDev"] = df["Close"].rolling(window=20).std()
df["VWAP+1STD"] = df["VWAP"] + df["StdDev"]
df["VWAP-1STD"] = df["VWAP"] - df["StdDev"]

# Calculate RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Compute RSI
df["RSI"] = compute_rsi(df["Close"])

# Create the plot
plt.style.use('classic')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})

# Plot VWAP and Price
ax1.plot(df.index, df["Close"], label="Close Price", color="blue", linewidth=1)
ax1.plot(df.index, df["VWAP"], label="VWAP", color="green", linewidth=1, linestyle="--")
ax1.fill_between(df.index, df["VWAP-1STD"], df["VWAP+1STD"], color="green", alpha=0.2, label="VWAP ± 1 STD")
ax1.set_title(f"{ticker} - VWAP Analysis", pad=20)
ax1.legend(loc="upper left")
ax1.grid(True, alpha=0.3)

# Plot RSI
ax2.plot(df.index, df["RSI"], label="RSI", color="purple", linewidth=1)
ax2.axhline(y=70, color="red", linestyle="--", alpha=0.5)
ax2.axhline(y=30, color="green", linestyle="--", alpha=0.5)
ax2.fill_between(df.index, 70, 30, color="gray", alpha=0.1)
ax2.set_ylim(0, 100)
ax2.set_title("RSI (14)", pad=20)
ax2.grid(True, alpha=0.3)

# Final adjustments
plt.tight_layout()
plt.show(block=True)

# Display relevant columns
display_columns = ["Close", "VWAP", "VWAP+1STD", "VWAP-1STD", "RSI"]
print(df[display_columns].tail(10))