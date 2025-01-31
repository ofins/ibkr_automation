import asyncio

from ib_insync import MarketOrder

from my_module.connect import disconnect_ib
from my_module.logger import Logger

logger = Logger.get_logger()


async def close_positions(ib, symbol):
    """
    Closes all active positions with MARKET order for a specific symbol.
    """
    try:
        # filter_active = [trade.orderId if hasattr(trade, 'orderId') else trade.order.orderId for trade in active_orders]
        
        cancel_tasks = []
        for order in ib.openOrders():
            # if order.orderId not in filter_active:
            #     continue
            try:
                # Some order types might not have a contract attribute
                # Create a task for each order cancellation
                cancel_task = asyncio.create_task(cancel_order_with_timeout(ib, order))
                logger.info(f"cancelled task: {cancel_task}")
                cancel_tasks.append(cancel_task)
            except Exception as order_cancel_error:
                logger.warning(f"Could not cancel order: {order_cancel_error}")
        
        # Wait for all cancellation tasks to complete
        if cancel_tasks:
            await asyncio.gather(*cancel_tasks)

        for pos in ib.positions():  
            if pos.contract.symbol != symbol:
                continue    
            
            contract = pos.contract
            contract.exchange = "SMART"
            order = MarketOrder(
                "SELL" if pos.position > 0 else "BUY", abs(pos.position)
            )
            trade = ib.placeOrder(contract, order)

            while not trade.isDone():
                await asyncio.sleep(1)
            logger.info(
                f"🚫 Position for {contract.localSymbol} with {abs(pos.position)} shares closed."
            )

        disconnect_ib(ib)
    except Exception as e:
        logger.error(f"Error during position closure: {e}")


async def cancel_order_with_timeout(ib, order, timeout=10):
    """
    Cancel an order with a timeout to prevent hanging
    """
    try:
        # Cancel the order
        ib.cancelOrder(order)
        
        # Wait for the order to be cancelled
        start_time = asyncio.get_event_loop().time()
        while not order.isActive():
            await asyncio.sleep(0.5)
            
            # Check for timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning(f"Order cancellation timed out: {order}")
                break
        
        logger.info(f"Order cancelled: {order}")
    except Exception as e:
        logger.warning(f"Error cancelling order: {e}")