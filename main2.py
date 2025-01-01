import asyncio

from ib_insync import IB

from my_module.logger import Logger
from my_module.trading_app import TradingApp

logger = Logger.get_logger(__name__)


def main():
    try:
        app = TradingApp()
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.error("Application terminated by user.")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")


if __name__ == "__main__":
    main()
