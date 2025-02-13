from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from my_module.logger import Logger

logger = Logger.get_logger()


def get_exit_time():
    est_time = ZoneInfo("America/New_York")
    now = datetime.now(est_time)
    # Holiday dates for 12:00 PM exit time
    holiday_dates = [(7, 3), (11, 26), (12, 24)]
    return time(12, 0) if (now.month, now.day) in holiday_dates else time(15, 45)

