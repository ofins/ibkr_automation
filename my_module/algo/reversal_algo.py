import asyncio

import aiohttp
import pandas as pd
import requests
from ib_insync import *
from tabulate import tabulate

from my_module.indicators import Indicators
from my_module.logger import Logger
from my_module.trade_input import WATCH_STOCK
from my_module.utils.candle_stick_chart import create_candle_chart
from my_module.utils.speak import Speak

logger = Logger.get_logger()
speak = Speak()


def fetch_historical_data(ib, contract):
    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr="1 D",
        barSizeSetting="3 mins",
        whatToShow="TRADES",
        useRTH=True,
        formatDate=1,
    )

    df = pd.DataFrame(
        [
            {
                "time": bar.date,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]
    )

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

    # columns_to_display = [
    #     "time",
    #     "close",
    #     "vwap",
    #     "vwap_upper",
    #     "vwap_lower",
    #     "rsi",
    # ]

    # logger.info(
    #     "\n"
    #     + tabulate(
    #         df[columns_to_display],
    #         headers="keys",
    #         tablefmt="fancy_grid",
    #         showindex=False,
    #     )
    # )

    return df


def calculate_suggested_price_levels(df, reversal_up):
    latest = df.iloc[-1]
    high_of_day = latest["high_of_day"]
    low_of_day = latest["low_of_day"]
    range = high_of_day - low_of_day

    suggested_entry = (
        low_of_day + range * 0.1 if reversal_up else high_of_day - range * 0.1
    )

    suggested_profit_target = (high_of_day + low_of_day) / 2

    suggested_stop = (
        suggested_entry - range / 4 if reversal_up else suggested_entry + range / 4
    )

    return suggested_entry, suggested_profit_target, suggested_stop


async def send_alert(alert_content, image_path):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/send-message",
            json={"content": alert_content, "image_path": image_path},
        ) as response:
            return await response.text()


async def check_alerts(ib, contract):

    df = fetch_historical_data(ib, contract)
    if len(df) < 1:
        return
    latest = df.iloc[-1]
    logger.info(contract.symbol)
    logger.info(latest)

    reversal_up = bool(
        latest["rsi"] <= 30
        and latest["open"] > latest["close"]
        and latest["close"] < latest["vwap_lower"]
    )
    # reversal_up = True

    reversal_down = bool(
        latest["rsi"] >= 70
        and latest["open"] < latest["close"]
        and latest["close"] > latest["vwap_upper"]
    )

    if reversal_up or reversal_down:
        suggested_entry, suggested_profit_target, suggested_stop = (
            calculate_suggested_price_levels(df, reversal_up)
        )
        image_path = await asyncio.to_thread(
            create_candle_chart,
            df,
            contract.symbol,
            suggested_entry,
            suggested_stop,
            suggested_profit_target,
        )

        alert_content = (
            f"📢 Trading Alert\n"
            f"📈 Symbol: {contract.symbol}\n"
            f"📅 Time: {latest['time']}\n"
            f"💰 Price: ${latest['close']:.2f}\n"
            f"📊 RSI: {latest['rsi']:.2f}\n"
            f"🔵 VWAP: {latest['vwap']:.2f}\n"
            f"🔺 Upper VWAP: {latest['vwap_upper']:.2f}\n"
            f"🔻 Lower VWAP: {latest['vwap_lower']:.2f}\n\n"
            f"{'🔼 Upward Reversal!\n' if reversal_up else '🔽 Downward Reversal!'}"
        )
        await send_alert(alert_content, image_path)

        direction = "UPWARD" if reversal_up else "DOWNWARD"
        logger.info(
            f"\n{direction} REVERSAL ALERT: {latest['time']} - ${latest['close']:.2f}"
        )
        speak.say(f"{direction.lower()} reversal alert!")


class ReversalAlgo:
    def __init__(self, ib, contract):
        self.ib = ib
        self.is_running = False
        self.contract = contract

    async def run(self):
        try:
            self.is_running = True
            while self.is_running:
                contracts = [
                    Stock("AAPL", "SMART", "USD"),
                    Stock("META", "SMART", "USD"),
                    Stock("AMD", "SMART", "USD"),
                    Stock("MU", "SMART", "USD"),
                    Stock("JPM", "SMART", "USD"),
                    Stock("TSLA", "SMART", "USD"),
                    Stock("SPY", "SMART", "USD"),
                ]
                tasks = [
                    asyncio.create_task(check_alerts(self.ib, contract))
                    for contract in contracts
                ]
                await asyncio.gather(*tasks)
                logger.info("checked...")
                self.ib.sleep(180)
        except KeyboardInterrupt:
            self.is_running = False
            raise
        finally:
            self.is_running = False
