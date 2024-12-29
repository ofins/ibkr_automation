import asyncio
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


async def timer(exit_time):
    est_time = ZoneInfo("America/New_York")
    print(exit_time)
    while datetime.now(est_time).time() < exit_time:
        print(f"Last validated time is {datetime.now(est_time).time()}")
        await asyncio.sleep(30)

    return 1
