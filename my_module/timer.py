import asyncio
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


async def timer(exit_time):
    est_time = ZoneInfo("America/New_York")
    logger.info(exit_time)

    while datetime.now(est_time).time() < exit_time:
        print(f"Time: {datetime.now(est_time).time()}")
        await asyncio.sleep(30)

    return 1
