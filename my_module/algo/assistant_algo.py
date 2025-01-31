from my_module.logger import Logger

logger = Logger.get_logger()


class AssistantAlgo:
    def __init__(self, ib):
        self.ib = ib
        self.active_orders = []
        self.is_running = False

    async def run(self):
        """
        Execute a simple trading strategy.
        """
        try:
            self.is_running = True
            positions = self.ib.positions()
            
            for pos in positions:
                if pos.contract.symbol in self.active_orders:
                    continue
            await self._cancel_active_orders()
            await self._close_positions()
        except Exception as e:
            logger.error(f"Error in trading strategy: {e}")
            raise
        finally:
            self.is_running = False
    