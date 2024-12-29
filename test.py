import asyncio
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from ib_insync import IB, MarketOrder, util

from connect import connect_ib

est_time = ZoneInfo("America/New_York")


ib = IB()


def get_exit_time():
    now = datetime.now(est_time)
    # Holiday dates for 12:00 PM exit time
    holiday_dates = [(7, 3), (11, 26), (12, 24)]
    return time(12, 0) if (now.month, now.day) in holiday_dates else time(15, 0)


async def close_all():

    if connect_ib() == 0:  # Connect to IBKR TWS
        print("Connection failed. Exiting.")
        return

    print(f"Connected. Monitoring until exit time: {get_exit_time()}")

    while datetime.now(est_time).time() < get_exit_time():
        print(f"Last validated time is {datetime.now(est_time).time()}")
        await asyncio.sleep(30)

    ib.reqGlobalCancel()  # Cancel all outstanding orders

    for pos in ib.positions():  # Exit all active trades
        contract = pos.contract
        contract.exchange = "SMART"
        order = MarketOrder("SELL" if pos.position > 0 else "BUY", abs(pos.position))
        trade = ib.placeOrder(contract, order)
        while not trade.isDone():
            await asyncio.sleep(1)
        print(
            f"Position for {contract.localSymbol} with {abs(pos.position)} shares closed."
        )

    ib.disconnect()


if __name__ == "__main__":
    asyncio.run(close_all())
