from typing import Union

from ib_insync import IB, LimitOrder, MarketOrder, Stock


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
    else:
        order = MarketOrder(action, quantity)

    trade = ib.placeOrder(contract, order)
    return trade
