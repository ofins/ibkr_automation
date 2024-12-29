import asyncio
from datetime import datetime, time, timedelta, timezone

from ib_insync import IB

from my_module.close_all_positions import close_all_positions
from my_module.connect import connect_ib
from my_module.data import Data
from my_module.logger import Logger
from my_module.price_action_algo import PriceActionAlgo
from my_module.timer import timer
from my_module.util import export_to_excel, generate_html_table, get_exit_time

logger = Logger.get_logger(__name__)

"""
This is the main module for the trading strategy.

It includes the core logic for connecting to the IBKR API, placing orders,
and handling the backtesting of the strategy.
"""


async def other_tasks():
    # Example async tasks function (replace with actual logic)
    logger.info("Running other tasks...")
    await asyncio.sleep(5)  # Simulate async task
    logger.info("Other tasks completed.")


async def main():
    # Ask the user for input
    print("Choose an option:")
    print("1. Run close trades timer")
    print("2. Fetch trades to Excel")
    print("3. Run Price Action Algo")

    choice = input("Enter your choice:")

    ib = IB()

    if await connect_ib(ib) == 0:
        logger.error("Failed to connect to IBKR. Exiting.")
        return

    logger.info("Connected to IBKR. Starting trading actions...")

    if choice == "1":

        timer_task = asyncio.create_task(timer(get_exit_time()))

        other_task = asyncio.create_task(other_tasks())

        result = await timer_task
        if result:
            logger.info("Timer finished. Proceed to close all positions...")
            await close_all_positions(ib)

        await other_task
    elif choice == "2":
        # fetch_all_trades_to_excel(ib)
        data = Data(ib)
        trades = data.get_session_trades()
        data.export_to_excel(trades)

        logger.info("Fetching ended. Exiting...")
        ib.disconnect()

    elif choice == "3":
        trader = PriceActionAlgo(ib)
        symbols = ["AAPL"]
        trader.run(symbols)

        isEnd = input("End ALGO now? Input 1 to end.")
        if isEnd == "1":
            ib.disconnect()
            return
    else:
        logger.error("Invalid choice. Exiting")
        ib.disconnect()
        return


if __name__ == "__main__":
    asyncio.run(main())
