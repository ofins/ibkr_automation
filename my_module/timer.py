import asyncio
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from my_module.close_all_positions import close_all_positions
from my_module.logger import Logger
from my_module.util import get_exit_time

logger = Logger.get_logger()


async def timer(exit_time):
    est_time = ZoneInfo("America/New_York")
    logger.info(f"Exit time: {exit_time}")

    while datetime.now(est_time).time() < exit_time:
        print(f"Time: {datetime.now(est_time).time()}")
        await asyncio.sleep(30)

    return 1


async def close_trades_timer(ib) -> None:
    try:
        exit_time = get_exit_time()
        timer_task = timer(exit_time)

        result = await timer_task
        if result:
            logger.info("Timer finished. Proceed to close all positions...")
            await close_all_positions(ib)
    except Exception as e:
        logger.error(f"Error in close trades operation: {str(e)}")
