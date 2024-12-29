from ib_insync import IB, MarketOrder, util

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


async def connect_ib(ib):
    """
    Connects to the IBKR TWS API.

    This function attempts to establish a connection with the Interactive
    Brokers Trader Workstation API, using a specified client ID and host.

    Returns:
        int: 1 if connection is successful, 0 if there is an error.
    """
    try:
        await ib.connectAsync("127.0.0.1", 7497, clientId=1)
        logger.info(f"Connected to IBKR tws API")
        return 1
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return 0
