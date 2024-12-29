import asyncio

from ib_insync import IB

from my_module.close_all_positions import close_all_positions
from my_module.connect import connect_ib
from my_module.timer import timer
from my_module.util import get_exit_time

"""
This is the main module for the trading strategy.

It includes the core logic for connecting to the IBKR API, placing orders,
and handling the backtesting of the strategy.
"""


async def main():
    ib = IB()

    if connect_ib(ib) == 0:
        print("Failed to connect to IBKR. Exiting.")
        return

    print("Connected to IBKR. Starting trading actions...")

    await timer(get_exit_time())
    await close_all_positions(ib)

    ib.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
