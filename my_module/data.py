from datetime import datetime, time, timedelta, timezone

import pandas as pd

from my_module.logger import Logger
from my_module.plot import mock_trades
from my_module.util import export_to_excel

logger = Logger.get_logger(__name__)


class Data:
    def __init__(self, ib):
        self.ib = ib

    def get_session_trades(self):
        trades = self.ib.trades()
        today_date = datetime.now().date()

        today_trades = [
            {
                "Symbol": trade.contract.symbol,
                "Action": trade.order.action,
                "Quantity": trade.order.totalQuantity,
                "Price": trade.order.lmtPrice,
                "Time": trade.filledTime,
                "Execution Price": trade.execution.avgPrice,
            }
            for trade in trades
            if trade.filledTime and trade.filledTime.date() == today_date
        ]

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
