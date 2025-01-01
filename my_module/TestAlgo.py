from ib_insync import MarketOrder, Stock

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


class TestAlgo:
    def __init__(self, ib):
        self.ib = ib

    def run(self):
        try:
            contract = Stock("AAPL", "SMART", "USD")
            order = MarketOrder("BUY", 25)

            self.ib.placeOrder(contract, order)
            logger.info(
                f"Place Order: {order.action} {order.totalQuantity} shares of {contract.symbol}"
            )
        except Exception as e:
            logger.error(f"Error during order placement: {e}")
