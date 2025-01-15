import asyncio
from decimal import Decimal
from typing import Literal

from ib_insync import MarketOrder, Stock, StopOrder

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


class TestAlgo:
    def __init__(self, ib):
        self.ib = ib
        self.stop_order = None

    async def run(
        self,
        symbol: str,
        direction: Literal["LONG", "SHORT"],
        initial_price: float,
        position_size: int,
        increment_range: float,
        stop_range: float,
        num_increments: int,
    ):
        """
        Execute a scaling strategy with stops.
        """
        try:
            contract = Stock(symbol, "SMART", "USD")

            # Determine order actions based on direction
            entry_action = "BUY" if direction == "LONG" else "SELL"
            exit_action = "SELL" if direction == "LONG" else "BUY"

            # Calculate all price levels first
            price_levels = []
            for i in range(num_increments):
                if direction == "LONG":
                    price = initial_price + (i * increment_range)
                else:
                    price = initial_price - (i * increment_range)
                price_levels.append(round(Decimal(str(price)), 2))

            logger.info(f"Calculated price levels: {price_levels}")

            stop_price = (
                float(price_levels[0]) - stop_range
                if direction == "LONG"
                else float(price_levels[0]) + stop_range
            )

            for price in price_levels:
                order = StopOrder(entry_action, position_size, price)
                self.ib.placeOrder(contract, order)

            while True:
                positions = self.ib.positions()
                for pos in positions:
                    logger.info(
                        f"Symbol: {pos.contract.symbol}, Size: {pos.position}, Avg Cost: {pos.avgCost}"
                    )

                    if float(pos.position) != 0:
                        if self.stop_order == None:
                            a = float(price_levels[0]) - increment_range
                            logger.info(a)

                            order = StopOrder(
                                exit_action,
                                pos.position,
                                a,
                            )

                            self.stop_order = self.ib.placeOrder(contract, order)
                            logger.info("2")

                        if float(self.stop_order.order.totalQuantity) == float(
                            pos.position
                        ):
                            return

                        self.ib.cancelOrder(self.stop_order.order)

                        await asyncio.sleep(3)

            # when price stop orders are filled, i want to put a stop loss of order with position equal to the total position size of this stock at the moment. It should update upon each stop order that is

        except Exception as e:
            logger.error(f"Error initializing scaling strategy: {e}")
            raise
