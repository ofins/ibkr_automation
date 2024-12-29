import asyncio

from ib_insync import IB

from my_module.close_all_positions import close_all_positions
from my_module.connect import connect_ib
from my_module.logger import Logger
from my_module.timer import timer
from my_module.util import get_exit_time

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
    ib = IB()

    if await connect_ib(ib) == 0:
        logger.error("Failed to connect to IBKR. Exiting.")
        return

    logger.info("Connected to IBKR. Starting trading actions...")

    timer_task = asyncio.create_task(timer(get_exit_time()))

    other_task = asyncio.create_task(other_tasks())

    result = await timer_task
    if result:
        logger.info("Timer finished. Proceed to close all positions...")
        await close_all_positions(ib)

    await other_task


if __name__ == "__main__":
    asyncio.run(main())
