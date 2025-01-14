import asyncio
from decimal import Decimal
from typing import Literal

from ib_insync import MarketOrder, Stock, StopOrder

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


class TestAlgo:
    def __init__(self, ib):
        self.ib = ib
        self.active_orders = {}  # Track active orders and their associated stops

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

            # Place stop loss order
            stop_order = StopOrder(
                exit_action,
                position_size,
                stop_price,
            )
            a = self.ib.placeOrder(contract, stop_order)
            logger.info(a.order.orderId)
            logger.info(f"Placed stop loss at {stop_price}")

            new_stop_order = StopOrder(
                exit_action,
                position_size,
                float(stop_price - 0.5),
            )

            # self.ib.placeOrder(contract, new_stop_order, orderId=a.order.orderId)

            # a.order.stopPrice = float(stop_price - 0.5)
            # self.ib.placeOrder(contract, a.order)

            # Place orders for each increment
            for i in range(num_increments):
                current_price = price_levels[i]
                next_price = price_levels[i + 1] if i < num_increments - 1 else None
                is_final = i == num_increments - 1

                logger.info(
                    f"Processing increment {i+1}/{num_increments} at price {current_price}"
                )

                await self._place_scaled_order(
                    contract=contract,
                    entry_action=entry_action,
                    exit_action=exit_action,
                    price_level=current_price,
                    position_size=position_size,
                    next_entry_price=next_price,
                    is_final=is_final,
                )

                # Wait a short time between placing orders to avoid rate limiting
                await asyncio.sleep(1)

            self.ib.cancelOrder(a.order)
            logger.info(
                f"Completed initialization of scaling {direction} strategy for {symbol}"
            )

        except Exception as e:
            logger.error(f"Error initializing scaling strategy: {e}")
            raise

    async def _place_scaled_order(
        self,
        contract,
        entry_action,
        exit_action,
        price_level,
        position_size,
        next_entry_price=None,
        is_final=False,
    ):
        """Place an entry order with associated stop loss and next entry order."""
        try:
            # Place entry order
            entry_order = MarketOrder(entry_action, position_size)
            trade = self.ib.placeOrder(contract, entry_order)

            # Wait for fill
            while not trade.isDone():
                await asyncio.sleep(0.1)

            if trade.orderStatus.status == "Filled":
                filled_price = trade.orderStatus.avgFillPrice
                logger.info(
                    f"Entry filled at {filled_price}: {entry_action} {position_size} shares of {contract.symbol}"
                )

                # If not final increment and we have a next entry price, place next entry stop order
                if not is_final and next_entry_price:
                    next_entry_stop = StopOrder(
                        entry_action, position_size, next_entry_price
                    )
                    self.ib.placeOrder(contract, next_entry_stop)
                    logger.info(f"Placed next entry stop at {next_entry_price}")

                await asyncio.sleep(0.1)  # Small delay after placing orders

        except Exception as e:
            logger.error(f"Error in scaled order placement: {e}")
            raise

    # def _calculate_stop_price(
    #     self, direction: str, entry_price: float, stop_range: float
    # ) -> float:
    #     """Calculate stop price based on direction and entry price."""
    #     if direction == "LONG":
    #         return round(Decimal(str(entry_price)) - Decimal(str(stop_range)), 2)
    #     return round(Decimal(str(entry_price)) + Decimal(str(stop_range)), 2)
