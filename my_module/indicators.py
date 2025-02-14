import pandas as pd


class Indicators:
    @staticmethod
    def calculate_rsi(df, periods=14):
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=periods).mean()
        avg_loss = loss.rolling(window=periods).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def vwap(df):
        cum_vol = df["volume"].cumsum()
        cum_vol_price = (df["volume"] * df["close"]).cumsum()
        return cum_vol_price / cum_vol

    @staticmethod
    def std_dev(df, periods=25):
        return df["close"].rolling(window=periods).std()

    @staticmethod
    def vwap_upper(df, std_dev):
        return df["vwap"] + std_dev

    @staticmethod
    def vwap_lower(df, std_dev):
        return df["vwap"] - std_dev

    @staticmethod
    def high_of_day(df, periods=390):
        return df["high"].rolling(window=periods).max()

    @staticmethod
    def low_of_day(df, periods=390):
        return df["low"].rolling(window=periods).min()

    @staticmethod
    def price_extension(df, open_price):
        (df["close"] - df["open"]) / open_price

    @staticmethod
    def volume_ma(df, periods=20):
        return df["volume"].rolling(window=periods).mean()

    @staticmethod
    def volume_trend(df, periods=20):
        return df["volume"] / df["volume"].rolling(window=periods).mean()

    # Trend detection
    @staticmethod
    def extended_up(df, extension=0.01):  # 1% up extension
        return df["price_extension"] > extension

    @staticmethod
    def extended_down(df, extension=-0.01):  # 1% down extension
        return df["price_extension"] < extension

    @staticmethod
    def breakout_upper_vwap(df):
        return df["close"] > df["vwap_upper"]

    @staticmethod
    def breakout_lower_vwap(df):
        return df["close"] < df["vwap_lower"]

    # determine trend
    @staticmethod
    def trend_up(df):
        return df["extended_up"] & df["breakout_upper_vwap"]

    @staticmethod
    def trend_down(df):
        return df["extended_down"] & df["breakout_lower_vwap"]
