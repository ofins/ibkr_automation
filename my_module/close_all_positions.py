import asyncio

from ib_insync import MarketOrder

from my_module.connect import disconnect_ib
from my_module.logger import Logger
from my_module.order import place_order

logger = Logger.get_logger(__name__)


async def close_all_positions(ib):
    """
    Closes all active positions with MARKET order.
    """
    try:
        logger.info("Cancelling all outstanding orders...")
        ib.reqGlobalCancel()
        for pos in ib.positions():  # Exit all active trades
            contract = pos.contract
            contract.exchange = "SMART"
            order = MarketOrder(
                "SELL" if pos.position > 0 else "BUY", abs(pos.position)
            )
            trade = ib.placeOrder(contract, order)

            while not trade.isDone():
                await asyncio.sleep(1)
            logger.info(
                f"Position for {contract.localSymbol} with {abs(pos.position)} shares closed."
            )

        disconnect_ib(ib)
    except Exception as e:
        logger.error(f"Error during position closure: {e}")
