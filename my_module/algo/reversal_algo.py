import asyncio

import numpy as np
import pandas as pd
import requests
from ib_insync import *
from tabulate import tabulate

from my_module.indicators import Indicators
from my_module.logger import Logger
from my_module.order import place_bracket_order
from my_module.trade_input import WATCH_STOCK
from my_module.utils.candle_stick_chart import create_candle_chart
from my_module.utils.speak import Speak

logger = Logger.get_logger()
speak = Speak()

url = "http://localhost:8000/send-message"

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
    "retrace_percentage",
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

    new_data = [
        {
            "time": bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "vwap": 0,
            "std_dev": 0,
            "vwap_upper": 0,
            "vwap_lower": 0,
            "price_extension": 0,
            "high_of_day": 0,
            "low_of_day": 0,
            "volume_ma": 0,
            "volume_trend": 0,
            "extended_up": 0,
            "extended_down": 0,
            "breakout_up": 0,
            "breakout_down": 0,
            "new_high": 0,
            "new_low": 0,
            "trend_up": False,
            "trend_down": False,
            "rsi": 0,
            "consolidating": 0,
            "reversal_up": False,
            "reversal_down": False,
            "retrace_percentage": 0,
            "retrace_level": 0,
        }
        for bar in bars
    ]

    df = pd.DataFrame(new_data)

    open_price = df.iloc[0]["open"]

    df["high_of_day"] = Indicators.high_of_day(df)
    df["low_of_day"] = Indicators.low_of_day(df)
    df["vwap"] = Indicators.vwap(df)
    df["std_dev"] = Indicators.std_dev(df)
    df["vwap_upper"] = Indicators.vwap_upper(df, df["std_dev"])
    df["vwap_lower"] = Indicators.vwap_lower(df, df["std_dev"])
    df["price_extension"] = Indicators.price_extension(df, open_price)
    df["volume_ma"] = Indicators.volume_ma(df)
    df["volume_trend"] = Indicators.volume_trend(df)
    df["extended_up"] = Indicators.extended_up(df)
    df["extended_down"] = Indicators.extended_down(df)
    df["rsi"] = Indicators.calculate_rsi(df)

    df["retrace_percentage"] = Indicators.retrace_percentage(
        df, open_price, "up" if df["close"].iloc[-1] > open_price else "down"
    )

    columns_to_display = [
        "time",
        "close",
        "vwap",
        "vwap_upper",
        "vwap_lower",
        "rsi",
    ]

    logger.info(
        "\n"
        + tabulate(
            df[columns_to_display],
            headers="keys",
            tablefmt="fancy_grid",
            showindex=False,
        )
    )

    return df


async def check_alerts(df):
    data = None
    logger.info("\nChecking for signals...")
    if len(df) < 1:
        return
    latest = df.iloc[-1]
    logger.info(latest)

    # requests.post(url, json=data)
    reversal_up = bool(
        latest["rsi"] <= 30
        and latest["open"] < latest["close"]
        and latest["close"] < latest["vwap_lower"]
    )

    reversal_down = bool(
        latest["rsi"] >= 70
        and latest["open"] > latest["close"]
        and latest["close"] > latest["vwap_upper"]
    )

    if reversal_up or reversal_down:
        image_path = await create_candle_chart(df)

        data = {
            "content": f"""
    >>> 📢 **Trading Alert**

    📈 **Symbol:** {WATCH_STOCK}  
    📅 **Time:** {latest['time']}  
    💰 **Price:** ${latest['close']:.2f}  
    📊 **RSI:** {latest['rsi']:.2f}  
    🔵 **VWAP:** {latest['vwap']:.2f}  
    🔺 **Upper VWAP:** {latest['vwap_upper']:.2f}  
    🔻 **Lower VWAP:** {latest['vwap_lower']:.2f}
            """,
            "image_path": image_path,
        }

    if reversal_up:
        logger.info("\nUPWARD REVERSAL ALERT 🔼")
        logger.info(f"Time: {latest['time']}")
        logger.info(f"Price: ${latest['close']:.2f}")
        speak.say("Upward reversal alert")
        data["content"] += "\n🔼 **Upward Reversal Detected!**"
        requests.post(url, json=data)
    if reversal_down:
        logger.info("\nDOWNWARD REVERSAL ALERT 🔽")
        logger.info(f"Time: {latest['time']}")
        logger.info(f"Price: ${latest['close']:.2f}")
        speak.say("Downward reversal alert")
        data["content"] += "\n🔽 **Downward Reversal Detected!**"
        requests.post(url, json=data)


class ReversalAlgo:
    def __init__(self, ib, contract):
        self.ib = ib
        self.is_running = False
        self.contract = contract

    async def run(self):
        try:
            self.is_running = True
            while self.is_running:
                data = fetch_historical_data(self.ib, self.contract)
                await check_alerts(data)
                self.ib.sleep(60 * 3)
        except KeyboardInterrupt:
            self.is_running = False
            raise
        finally:
            self.is_running = False
