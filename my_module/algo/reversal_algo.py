import asyncio

import numpy as np
import pandas as pd
from ib_insync import *

from my_module.indicators import Indicators

columns = [
    "time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",
    "std_dev",
    "vwap_upper",
    "vwap_lower",
    "price_extension",
    "high_of_day",
    "low_of_day",
    "volume_ma",
    "volume_trend",
    "extended_up",
    "extended_down",
    "breakout_up",
    "breakout_down",
    "new_high",
    "new_low",
    "trend_up",
    "trend_down",
    "rsi",
    "consolidating",
    "reversal_up",
    "reversal_down",
]

df = pd.DataFrame(columns=columns)


def fetch_historical_data(ib, contract):
    global df
    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr="1 D",
        barSizeSetting="3 mins",
        whatToShow="TRADES",
        useRTH=True,
        formatDate=1,
    )
    # print(bars)

    new_data = [
        {
            "time": bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "vwap": np.nan,
            "std_dev": np.nan,
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
            "reversal_down": np.nan,
        }
        for bar in bars
    ]

    df = pd.DataFrame(new_data)

    df["vwap"] = Indicators.vwap(df)
    df["std_dev"] = Indicators.std_dev(df)
    df["vwap_upper"] = Indicators.vwap_upper(df, df["std_dev"])
    df["vwap_lower"] = Indicators.vwap_lower(df, df["std_dev"])
    df["high_of_day"] = Indicators.high_of_day(df)
    df["low_of_day"] = Indicators.low_of_day(df)
    df["price_extension"] = Indicators.price_extension(df, df.iloc[0]["open"])
    df["volume_ma"] = Indicators.volume_ma(df)
    df["volume_trend"] = Indicators.volume_trend(df)
    df["extended_up"] = Indicators.extended_up(df)
    df["extended_down"] = Indicators.extended_down(df)
    df["breakout_upper_vwap"] = Indicators.breakout_upper_vwap(df)
    df["breakout_lower_vwap"] = Indicators.breakout_lower_vwap(df)
    df["trend_up"] = Indicators.trend_up(df)
    df["trend_down"] = Indicators.trend_down(df)

    check_alerts()


def check_alerts():
    if len(df) < 1:
        return
    latest = df.iloc[-1]
    print(latest)

    if latest["reversal_up"] is True:
        print("\nUPWARD REVERSAL ALERT 🔼")
        print(f"Time: {latest['time']}")
        print(f"Price: ${latest['close']:.2f}")

    if latest["reversal_down"] is True:
        print("\nDOWNWARD REVERSAL ALERT 🔽")
        print(f"Time: {latest['time']}")
        print(f"Price: ${latest['close']:.2f}")


class ReversalAlgo:
    def __init__(self, ib):
        self.ib = ib
        self.is_running = False
        self.contract = Stock("AAPL", "SMART", "USD")

    async def run(self):
        fetch_historical_data(self.ib, self.contract)

        try:
            self.is_running = True
            while self.is_running:
                # await asyncio.sleep(5)
                await self.ib.sleep(5)
                # self.ib.sleep(5)
                # pass
        except KeyboardInterrupt:
            self.is_running = False
            raise
        finally:
            self.is_running = False
