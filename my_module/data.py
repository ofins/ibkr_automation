from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


class Data:
    def __init__(self, ib):
        self.ib = ib

    def get_session_trades(self):
        trades = self.ib.trades()
        today_date = (
            datetime.now(timezone.utc).astimezone().date()
        )  # Ensure timezone-awareness

        today_trades = []
        for trade in trades:
            # Check if there are fills and extract the filled time
            if trade.fills:
                filled_time = trade.fills[
                    0
                ].execution.time  # Assuming the first fill represents the trade's filled time

                if filled_time.date() == today_date:
                    logger.info(trade.fills[0].execution)
                    today_trades.append(
                        {
                            "Symbol": trade.contract.symbol,
                            "Action": trade.order.action,
                            "Quantity": trade.fills[0].execution.shares,
                            "Price": trade.order.lmtPrice,
                            "Time": trade.fills[0]
                            .execution.time.astimezone(ZoneInfo("America/New_York"))
                            .strftime("%Y-%m-%d %H:%M:%S"),
                            "Execution Price": trade.fills[0].execution.avgPrice,
                            "Realized PNL": trade.fills[0].commissionReport.realizedPNL,
                        }
                    )

        if not today_trades:
            logger.info("No trades found for this session")
            return []

        return today_trades

    def export_to_excel(self, data, file_name):
        if not data:
            logger.error("No data provided to export")
            return

        df = pd.DataFrame(data)

        try:
            df.to_excel(file_name, index=False)
            logger.info(f"Today's trades saved to {file_name}")
        except Exception as e:
            logger.error(f"Error saving trades to Excel: {e}")
