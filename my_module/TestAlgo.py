import asyncio
from decimal import Decimal
from typing import Literal

from ib_insync import LimitOrder, MarketOrder, Stock, StopOrder

from my_module.close_all_positions import close_all_positions
from my_module.logger import Logger

logger = Logger.get_logger(__name__)


class TestAlgo:
    def __init__(self, ib):
        self.ib = ib
        self.active_orders = []
        self.stop_order = None
        self.is_running = False
        self.exit_action = None
        self.entry_action = None
        self.is_active_trading = False

    async def run(
        self,
        symbol: str,
        direction: Literal["LONG", "SHORT"],
        initial_price: float,
        position_size: int,
        increment_range: float,
        num_increments: int,
    ):
        """
        Execute a scaling strategy with stops.

        Args:
            symbol: Trading symbol
            direction: Trade direction ("LONG" or "SHORT")
            initial_price: Starting price level
            position_size: Size of each position increment
            increment_range: Price difference between levels
            num_increments: Number of scaling levels
        """
        try:
            self.is_running = True
            contract = Stock(symbol, "SMART", "USD")

            self._set_order_actions(direction)

            price_levels = self._calculate_price_levels(
                direction, initial_price, increment_range, num_increments
            )
            logger.info(f"Calculated price levels: {price_levels}")

            await self._place_entry_orders(
                contract, position_size, price_levels, increment_range, num_increments
            )

            await self._monitor_positions(
                contract, self.exit_action, price_levels, increment_range, direction
            )

        except Exception as e:
            logger.error(f"Error in trading strategy: {e}")
            await self.cleanup()
            raise
        finally:
            self.is_running = False

    def _calculate_price_levels(
        self,
        direction: str,
        initial_price: float,
        increment_range: float,
        num_increments: int,
    ) -> list[Decimal]:
        """Calculate all price levels for scaling in."""
        return [
            round(Decimal(str(initial_price + (i * increment_range) if direction == "LONG" else initial_price - (i * increment_range))), 2)
            for i in range(num_increments)
        ]

    def _set_order_actions(self, direction: str):
        """Set entry and exit actions based on trade direction."""
        self.entry_action = "BUY" if direction == "LONG" else "SELL"
        self.exit_action = "SELL" if direction == "LONG" else "BUY"

    async def _place_entry_orders(
        self,
        contract,
        position_size: int,
        price_levels: list[Decimal],
        increment_range: float,
        num_increment: int,
    ):
        """Place all entry orders at calculated price levels."""
        for price in price_levels:
            order = StopOrder(self.entry_action, position_size, price)
            placed_order = self.ib.placeOrder(contract, order)
            self.active_orders.append(placed_order)


        exit_profit_price = price_levels[-1] + Decimal(str(increment_range)) if self.entry_action == "BUY" else price_levels[-1] - Decimal(str(increment_range))
        limitOrder = LimitOrder(self.exit_action, position_size * num_increment, exit_profit_price)
        place_profit_target = self.ib.placeOrder(contract, limitOrder)
        self.active_orders.append(place_profit_target)

    async def _monitor_positions(
        self,
        contract,
        exit_action: str,
        price_levels: list[Decimal],
        increment_range: float,
        direction: str,
    ):
        """Monitor positions and manage stop orders."""
        while self.is_running:
            try:
                current_position = self._get_current_position(contract)

                if current_position != 0:
                    await self._manage_stop_order(
                        contract,
                        exit_action,
                        current_position,
                        price_levels,
                        increment_range,
                        direction,
                    )
                    self.is_active_trading = True

                if self.is_active_trading and current_position == 0:
                    logger.info("All positions closed. Exiting position monitoring.")
                    await close_all_positions(self.ib)
                    await self.cleanup()
                    break

                await asyncio.sleep(1)  # Reduce polling frequency

            except Exception as e:
                logger.error(f"Error in position monitoring: {e}")
                await self.cleanup()
                break

    def _get_current_position(self, contract) -> float:
        """Get current position size for the contract."""
        positions = self.ib.positions()
        for pos in positions:
            if pos.contract.symbol == contract.symbol:
                return float(pos.position)
        return 0

    async def _manage_stop_order(
        self,
        contract,
        exit_action: str,
        current_position: float,
        price_levels: list[Decimal],
        increment_range: float,
        direction: str,
    ):
        """Manage the stop order based on current position."""
        stop_price = self._calculate_stop_price(
            price_levels[0], increment_range, direction
        )

        if self.stop_order is None:
            self.stop_order = self.ib.placeOrder(
                contract, StopOrder(exit_action, abs(current_position), stop_price)
            )
            logger.info(f"Placed new stop order at {stop_price}")

        elif abs(float(self.stop_order.order.totalQuantity)) != abs(current_position):
            # Update stop order if position size has changed
            self.ib.cancelOrder(self.stop_order.order)
            await asyncio.sleep(1)  # Wait for cancellation to process

            self.stop_order = self.ib.placeOrder(
                contract, StopOrder(exit_action, abs(current_position), stop_price)
            )
            logger.info(
                f"Updated stop order to match position size: {current_position}"
            )

    def _calculate_stop_price(
        self, base_price: Decimal, increment_range: float, direction: str
    ) -> float:
        """Calculate stop price based on direction and base price."""
        return float(base_price) - increment_range if direction == "LONG" else float(base_price) + increment_range


    async def cleanup(self):
        """Cancel all active orders."""
        for order in self.active_orders:
            try:
                self.ib.cancelOrder(order.order)
            except Exception as e:
                logger.error(f"Error cancelling order: {e}")

        if self.stop_order:
            try:
                self.ib.cancelOrder(self.stop_order.order)
            except Exception as e:
                logger.error(f"Error cancelling stop order: {e}")

        self.active_orders = []
        self.stop_order = None
