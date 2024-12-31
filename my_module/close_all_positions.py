import asyncio

from ib_insync import MarketOrder

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
            action = "SELL" if pos.position > 0 else "BUY"
            trade = place_order(ib, contract, action, abs(pos.position), "MARKET")

            while not trade.isDone():
                await asyncio.sleep(1)
            logger.info(
                f"Position for {contract.localSymbol} with {abs(pos.position)} shares closed."
            )

        ib.disconnect()
    except Exception as e:
        logger.error(f"Error during position closure: {e}")
