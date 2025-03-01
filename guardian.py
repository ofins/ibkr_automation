import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, time
from functools import reduce
from zoneinfo import ZoneInfo

import pandas as pd
from ib_insync import IB

from my_module.close_all_positions import close_all_positions
from my_module.connect import connect_ib
from my_module.logger import Logger

logger = Logger.get_logger()


@dataclass
class Config:
    EXIT_TIME = "15:45:00"
    MAX_POSITION_SIZE = 50
    MAX_OPEN_POSITIONS = 7
    MAX_TRADES_PER_DAY = 20
    MAX_DAILY_DRAWDOWN = -200
    TIMEZONE = ZoneInfo("America/New_York")
    TURN_OFF_TIMER = False


class Timer:
    @staticmethod
    def get_exit_time():
        now = datetime.now(Config.TIMEZONE)
        # Holiday dates for 12:00 PM exit time
        holiday_dates = [(7, 3), (11, 26), (12, 24)]
        return time(12, 0) if (now.month, now.day) in holiday_dates else time(15, 45)

    @staticmethod
    async def check_exit_time(ib):
        exit_time = Timer.get_exit_time()
        logger.info(f"Current time: {datetime.now(Config.TIMEZONE).time()}")
        if Config.TURN_OFF_TIMER:
            return
        if datetime.now(Config.TIMEZONE).time() > exit_time:
            logger.info(f"Timer reached: {Config.EXIT_TIME} . Closing all positions...")
            await close_all_positions(ib)
            raise KeyboardInterrupt


class Account:
    """Account keeps track of my portfolio and account details."""

    # Monitor drawdowns
    @staticmethod
    async def check_daily_pnl(ib):
        account_summary = await ib.accountSummaryAsync()
        df = pd.DataFrame(account_summary)
        realized_pnl = df[df.tag == "RealizedPnL"].iloc[0].value
        logger.info(f"Realized PnL: {realized_pnl} | {Config.MAX_DAILY_DRAWDOWN}")
        if float(realized_pnl) < Config.MAX_DAILY_DRAWDOWN:
            logger.info(f"Daily drawdown exceeded: {realized_pnl}. Closing trades.")
            await close_all_positions(ib)

    # Monitor open positions
    @staticmethod
    async def check_open_positions(ib):
        positions = ib.positions()
        logger.info(
            f"Total open positions: {len(positions)} | {Config.MAX_OPEN_POSITIONS}"
        )
        if len(positions) > Config.MAX_OPEN_POSITIONS:
            logger.info(f"Max positions exceeded: {len(positions)}. Closing trades.")
            await close_all_positions(ib)

    # Monitor position sizes
    @staticmethod
    async def check_position_sizes(ib):
        positions = ib.positions()
        total_size = reduce(lambda a, b: a + b, [p.position for p in positions], 0)
        logger.info(f"Total position size: {total_size}")
        for pos in positions:
            if pos.position > Config.MAX_POSITION_SIZE:
                logger.info(
                    f"Position size exceeded: {pos.contract.symbol} - {pos.position}. Closing trades."
                )
                await close_all_positions(ib)

    # Monitor daily trades
    @staticmethod
    async def check_daily_trades(ib):
        trades = ib.trades()
        logger.info(f"Total trades today: {len(trades)} | {Config.MAX_TRADES_PER_DAY}")
        if len(trades) > Config.MAX_TRADES_PER_DAY:
            logger.info(f"Max trades exceeded: {len(trades)}. Closing trades.")
            await close_all_positions(ib)


class Guardian:
    """Guardian ensures my assets are safe from over-exposure and unexpected events."""

    def __init__(self, ib, config: Config):
        self.config = config
        self.ib = ib

    async def run(self) -> None:
        await connect_ib(self.ib)

        # Main monitoring loop
        while True:
            try:
                tasks = [
                    Timer.check_exit_time(self.ib),
                    Account.check_daily_pnl(self.ib),
                    Account.check_open_positions(self.ib),
                    Account.check_position_sizes(self.ib),
                    Account.check_daily_trades(self.ib),
                ]

                await asyncio.gather(*tasks)
                print("=" * 40)
                # Wait before next check
                await asyncio.sleep(30)
            except KeyboardInterrupt:
                logger.info("Keyboard Interrupt.")
                break
            except Exception as e:
                logger.error(f"Error in Guardian monitoring: {str(e)}")
                await asyncio.sleep(30)  # Continue monitoring even after error


if __name__ == "__main__":
    ib = IB()
    guardian = Guardian(ib, Config)
    asyncio.run(guardian.run())
