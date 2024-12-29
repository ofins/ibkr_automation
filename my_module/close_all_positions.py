from ib_insync import MarketOrder

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


async def close_all_positions(ib):
    """
    Closes all active positions.
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

        ib.disconnect()
    except Exception as e:
        logger.error(f"Error during position closure: {e}")
