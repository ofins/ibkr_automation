import asyncio
from typing import Union

from ib_insync import IB, LimitOrder, MarketOrder, Stock, StopOrder

from my_module.connect import connect_ib, disconnect_ib
from my_module.logger import Logger

logger = Logger.get_logger()


def place_order(
    ib: IB,
    contract: Stock,
    action: str,
    quantity: int,
    order_type: str = "MARKET",
    price: Union[float, None] = None,
):
    """
    Places an order using the provided parameters.

    :param ib: The connected IB instance (ib_insync.IB).
    :param contract: The stock contract to trade (ib_insync.Stock).
    :param action: Action to perform ('BUY' or 'SELL').
    :param quantity: The number of shares/contracts to trade.
    :param order_type: Type of the order ('MARKET' or 'LIMIT'). Default is 'MARKET'.
    :param price: The limit price if using a limit order. Default is None for market orders.

    :return: The placed order.
    """
    if order_type.upper() == "LIMIT" and price is not None:
        order = LimitOrder(action, quantity, price)
    elif order_type.upper() == "STOP":
        order = StopOrder(action, quantity, price)
    else:
        order = MarketOrder(action, quantity)

    trade = ib.placeOrder(contract, order)
    return trade


def place_bracket_order(
    ib: IB,
    contract: Stock,
    action: str,
    quantity: int,
    entry_price: float,
    take_profit: float,
    stop_loss: float,
):
    bracket = ib.bracketOrder(
        action,
        quantity,
        *(round(price, 2) for price in (entry_price, take_profit, stop_loss)),
    )
    for o in bracket:
        ib.placeOrder(contract, o)
    return bracket


async def main():
    ib = IB()
    try:
        await connect_ib(ib)
        contract = Stock("AAPL", "SMART", "USD")
        place_bracket_order(ib, contract, "BUY", 1, 259.355, 245, 244.5)
    finally:
        disconnect_ib(ib)


if __name__ == "__main__":
    """Example usage of placing an order."""

    asyncio.run(main())
