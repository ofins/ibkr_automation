import asyncio
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp
import pandas as pd
import requests
from ib_insync import *
from tabulate import tabulate

from my_module.close_all_positions import close_all_positions
from my_module.connect import connect_ib
from my_module.indicators import Indicators
from my_module.logger import Logger
from my_module.order import place_bracket_order
from my_module.util import get_exit_time
from my_module.utils.candle_stick_chart import create_candle_chart
from my_module.utils.speak import Speak

logger = Logger.get_logger()
speak = Speak()


@dataclass
class Config:
    """Configuration class for the reversal algo."""

    HISTORICAL_DURATION: str = "2 D"
    BAR_SIZE: str = "3 mins"
    CHECK_INTERVAL_SECONDS: int = 180
    # CONTRACTS = ["AAPL", "META", "AMD", "MU", "JPM", "TSLA", "SPY"]
    CONTRACTS = ["TSLA"]


class HistoricalDataFetcher:
    """Handles fetching historical data for a given stock symbol."""

    @staticmethod
    def fetch(ib: IB, contract: Contract, config: Config) -> pd.DataFrame:
        bars = ib.reqHistoricalData(
            contract,
            # endDateTime="20250226 05:00:00",
            endDateTime="",
            durationStr="2 D",
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

        return HistoricalDataFetcher._add_indicators(df)

    @staticmethod
    def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""

        open_price = df.iloc[0]["open"]
        today_date = df["time"].iloc[-1].normalize()
        df_today = df[df["time"].dt.normalize() == today_date]

        df["high_of_day"] = Indicators.high_of_day(df_today)
        df["low_of_day"] = Indicators.low_of_day(df_today)
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
        df["breakout_upper_vwap"] = Indicators.breakout_upper_vwap(df)
        df["breakout_lower_vwap"] = Indicators.breakout_lower_vwap(df)
        df["retrace_percentage"] = Indicators.retrace_percentage(
            df, open_price, "up" if df["close"].iloc[-1] > open_price else "down"
        )

        columns_to_display = [
            "time",
            "close",
            "high_of_day",
            "low_of_day",
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


class PriceLevelCalculator:
    """Calculates suggested price levels for a given stock symbol."""

    @staticmethod
    def calculate(df: pd.DataFrame, reversal_up: bool):
        latest = df.iloc[-1]
        high_of_day = latest["high_of_day"]
        low_of_day = latest["low_of_day"]
        range = high_of_day - low_of_day
        close = latest["close"]

        suggested_entry = (
            min(low_of_day + (range * 0.1), close)
            if reversal_up
            else max(high_of_day - (range * 0.1), close)
        )
        suggested_profit_target = (high_of_day + low_of_day) / 2
        suggested_stop = (
            suggested_entry - range / 4 if reversal_up else suggested_entry + range / 4
        )

        return suggested_entry, suggested_profit_target, suggested_stop


class AlertManager:
    """Manages alerts for trend reversal."""

    @staticmethod
    async def send_alert(alert_content, image_path):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/send-message",
                json={"content": alert_content, "image_path": image_path},
            ) as response:
                return await response.text()

    @staticmethod
    def create_alert_content(
        contract: Contract,
        latest: pd.Series,
        reversal_up: bool,
        entry: float,
        profit_target: float,
        stop: float,
    ) -> str:
        risk_reward = abs(profit_target - entry) / abs(stop - entry)

        return (
            f"📢 Trading Alert\n"
            f"📈 Symbol: {contract.symbol}\n"
            f"📅 Time: {latest['time']}\n"
            f"💰 Price: ${latest['close']:.2f}\n"
            f"📈 High of Day: ${latest['high_of_day']:.2f}\n"
            f"📉 Low of Day: ${latest['low_of_day']:.2f}\n"
            f"📊 RSI: {latest['rsi']:.2f}\n"
            f"🔵 VWAP: {latest['vwap']:.2f}\n"
            f"🔺 Upper VWAP: {latest['vwap_upper']:.2f}\n"
            f"🔻 Lower VWAP: {latest['vwap_lower']:.2f}\n\n"
            f"{'🔼 Upward Reversal!\n' if reversal_up else '🔽 Downward Reversal!\n'}"
            f"⚖️ Risk Reward Ratio: {risk_reward:.2f}"
        )


class ReversalAlgo:
    def __init__(self, ib: IB, config: Config = Config()):
        self.ib = ib
        self.config = config
        self.is_running = False
        self.contracts = [
            Stock(symbol, "SMART", "USD") for symbol in self.config.CONTRACTS
        ]

    async def check_alerts(self, contract: Contract) -> None:
        """Check for trading alerts for specific contract"""
        try:
            df = HistoricalDataFetcher.fetch(self.ib, contract, self.config)
            if df.empty:
                return

            prev, last = df.iloc[-2], df.iloc[-1]

            reversal_up = (
                last["rsi"] > 30 and prev["rsi"] < 30 and last["breakout_lower_vwap"]
            )
            # reversal_up = True
            reversal_down = (
                last["rsi"] < 70 and prev["rsi"] > 70 and last["breakout_upper_vwap"]
            )

            if reversal_up or reversal_down:
                await self.handle_reversal(contract, df, last, reversal_up)
        except Exception as e:
            logger.error(f"Error in checking alerts for {contract.symbol}: {str(e)}")

    async def handle_reversal(
        self, contract: Contract, df: pd.DataFrame, latest: pd.Series, reversal_up: bool
    ) -> None:
        """Handle a detected reversal"""
        entry, profit_target, stop = PriceLevelCalculator.calculate(df, reversal_up)

        image_path = await asyncio.to_thread(
            create_candle_chart,
            df,
            contract.symbol,
            entry,
            stop,
            profit_target,
        )

        alert_content = AlertManager.create_alert_content(
            contract, latest, reversal_up, entry, profit_target, stop
        )

        place_bracket_order(
            self.ib,
            contract,
            "BUY" if reversal_up else "SELL",
            1,
            entry,
            profit_target,
            stop,
        )

        direction = "UPWARD" if reversal_up else "DOWNWARD"
        await AlertManager.send_alert(alert_content, image_path)
        speak.say(f"{direction.lower()} reversal")
        speak.say_letter_by_letter(contract.symbol)

    async def run(self):
        """Main algo execution loop"""
        try:
            self.is_running = True

            while self.is_running:
                # Do not check alerts for active position stocks
                active_symbols = {
                    pos.contract.symbol.upper() for pos in self.ib.positions()
                }

                tasks = [
                    self.check_alerts(contract)
                    for contract in self.contracts
                    if contract.symbol.upper() not in active_symbols
                ]

                await asyncio.gather(*tasks)
                logger.info(f"Monitored:{self.config.CONTRACTS}")
                self.ib.sleep(self.config.CHECK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Error in running reversal algo: {str(e)}")
        finally:
            self.is_running = False


async def main():
    """Application entry point"""
    try:
        ib = IB()
        await connect_ib(ib)

        algo = ReversalAlgo(ib)
        await algo.run()
    finally:
        ib.disconnect()


# Testing
if __name__ == "__main__":
    asyncio.run(main())
