import numpy as np
import pandas as pd

from my_module.logger import Logger

logger = Logger.get_logger()


class Indicators:
    @staticmethod
    def calculate_rsi(df, periods=14):
        delta = df["close"].diff()
        gain, loss = delta.copy(), delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = -loss

        def rma(x, n):
            alpha = 1 / n
            return x.ewm(alpha=alpha, adjust=False).mean()  # ✅ Fix: Add parentheses

        avg_gain = rma(gain, periods)  # ✅ Now returns actual values
        avg_loss = rma(loss, periods)

        rs = avg_gain / avg_loss  # ✅ Now dividing numbers, not methods
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def vwap(df):
        cum_vol = df["volume"].cumsum()
        cum_vol_price = (df["volume"] * df["close"]).cumsum()
        return cum_vol_price / cum_vol

    @staticmethod
    def std_dev(df):
        squared_deviation = (df["close"] - df["vwap"]) ** 2
        periods = pd.Series(range(1, len(df) + 1))
        vwap_variance = squared_deviation.cumsum() / periods
        vwap_std = np.sqrt(vwap_variance)
        return vwap_std

    @staticmethod
    def vwap_upper(df, std_dev):
        return df["vwap"] + std_dev * 1

    @staticmethod
    def vwap_lower(df, std_dev):
        return df["vwap"] - std_dev * 1

    @staticmethod
    def high_of_day(df):
        return df["high"].max()

    @staticmethod
    def low_of_day(df):
        return df["low"].min()

    @staticmethod
    def price_extension(df, open_price):
        return (df["close"] - df["open"]) / open_price

    @staticmethod
    def volume_ma(df, periods=20):
        return df["volume"].rolling(window=periods).mean()

    @staticmethod
    def volume_trend(df, periods=20):
        return df["volume"] / df["volume"].rolling(window=periods).mean()

    # Trend detection
    @staticmethod
    def extended_up(df, extension=0.01):  # 1% up extension
        return (df["price_extension"] > extension).any()

    @staticmethod
    def extended_down(df, extension=-0.01):  # 1% down extension
        return (df["price_extension"] < extension).any()

    @staticmethod
    def breakout_upper_vwap(df):
        return df["close"] > df["vwap_upper"]

    @staticmethod
    def breakout_lower_vwap(df):
        return df["close"] < df["vwap_lower"]

    # determine trend
    @staticmethod
    def trend_up(df):
        return df["breakout_upper_vwap"]

    @staticmethod
    def trend_down(df):
        return df["breakout_lower_vwap"]

    # Reversal detection
    @staticmethod
    def retrace_percentage(df, open_price, direction):
        high_of_day = df["high_of_day"]
        current_price = df["close"]

        if direction == "up":
            retrace_percentage = (current_price - open_price) / (
                high_of_day - open_price
            )
        elif direction == "down":
            retrace_percentage = (high_of_day - current_price) / (
                high_of_day - open_price
            )
        else:
            raise ValueError("Invalid direction")

        return retrace_percentage

    @staticmethod
    def reversal_up(df):
        return (df["retrace_percentage"] < 0.85) & df["trend_down"]

    @staticmethod
    def reversal_down(df):
        return (df["retrace_percentage"] < 0.85) & df["trend_up"]
