from datetime import datetime, time, timedelta, timezone

from my_module.logger import Logger
from my_module.plot import mock_trades
from my_module.util import export_to_excel

logger = Logger.get_logger(__name__)


def fetch_all_trades_to_excel(ib):
    trades = ib.trades()  # Fetch all trades from this session
    today = datetime.now().date()
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
        if trade.filledTime and trade.filledTime.date() == today
    ]

    # today_trades = mock_trades

    if not today_trades:
        logger.info("No trades found for today")
        return

    export_to_excel(today_trades, f"{today.strftime("%Y-%m-%d")}.xlsx")
