from my_module.util import export_to_excel


def fetch_all_trades_to_excel(ib):
    trades = ib.trades()

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

    if not today_trades:
        logger.info("No trades found for today")
        return

    export_to_excel(today_trades, today.strftime("%Y-%m-%d"))
