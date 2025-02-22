import asyncio
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Coroutine, Dict, Optional, Union

import nest_asyncio
from ib_insync import *

import my_module.trade_input as trade_input
from my_module.algo.reversal_algo import ReversalAlgo
from my_module.algo.scaling_in_algo import ScalingInAlgo
from my_module.close_all_positions import close_all_positions
from my_module.connect import connect_ib, disconnect_ib
from my_module.data import Data
from my_module.instance import Instance
from my_module.logger import Logger
from my_module.plot import generate_html
from my_module.timer import timer
from my_module.util import get_exit_time
from my_module.utils.arg_parser import args

nest_asyncio.apply()

logger = Logger.get_logger()


class MenuOption(Enum):
    CLOSE_TRADES = auto()  # Close all traders / orders at a specific time
    FETCH_TRADES = auto()  # Generate trade report
    SCALE_IN_ALGO = auto()  # place orders / monitor stop
    REVERSAL_ALGO = auto()  # detect trend reversal
    EXIT = auto()


@dataclass
class MenuChoice:
    option: MenuOption
    description: str


instance = Instance()
instance.set_symbol(trade_input.SYMBOL)


class TradingApp:
    """Main trading application that handles IBKR connectivity and trading operations."""

    MENU_CHOICES = {
        "1": MenuChoice(MenuOption.CLOSE_TRADES, "Run close trades timer"),
        "2": MenuChoice(MenuOption.FETCH_TRADES, "Generate trade report"),
        "3": MenuChoice(MenuOption.SCALE_IN_ALGO, "Run Scale-in algo"),
        "4": MenuChoice(MenuOption.REVERSAL_ALGO, "Run Reversal algo"),
        "5": MenuChoice(MenuOption.EXIT, "Exit"),
    }

    def __init__(self):
        self.ib = IB()
        self.data: Data | None = None

    async def display_menu(self) -> MenuOption | None:
        print("\nTrading Application Menu:")
        for key, choice in self.MENU_CHOICES.items():
            print(f"{key}. {choice.description}")

        try:
            user_input = args.menu or input("\nEnter your choice: ").strip()
            return self.MENU_CHOICES[user_input].option
        except KeyError:
            if user_input:
                logger.error("Invalid menu choice.")
            return None

    async def close_trades(self) -> None:
        try:
            exit_time = get_exit_time()
            timer_task = timer(exit_time)

            result = await timer_task
            if result:
                logger.info(
                    "Timer finished. Proceed to close all positions...")
                await close_all_positions(self.ib)

            await self.fetch_trades()
        except Exception as e:
            logger.error(f"Error in close trades operation: {str(e)}")

    async def fetch_trades(self) -> None:
        try:
            if not self.data:
                self.data = Data(self.ib)

            trades = self.data.get_session_trades()
            generate_html(trades)
            # TODO: save data in postgres SQL
            Logger.separator("📈 Successfully generated report.")
        except Exception as e:
            logger.error(f"Error in generating report: {str(e)}")

    async def run_scale_in_algo(self) -> None:
        try:
            trader = ScalingInAlgo(self.ib, instance)
            await trader.run(
                trade_input.SYMBOL,
                trade_input.DIRECTION,
                trade_input.ENTRY_PRICE,
                trade_input.POSITION_SIZE,
                trade_input.INCREMENT_RANGE,
                trade_input.NUM_INCREMENTS,
            )
            await self.fetch_trades()
        except Exception as e:
            logger.error(f"Error in running test algo: {str(e)}")

    async def run_reversal_algo(self) -> None:
        stock = Stock(trade_input.WATCH_STOCK, "SMART", "USD")
        try:
            reversal = ReversalAlgo(self.ib, stock)
            await reversal.run()
        except Exception as e:
            logger.error(f"Error in running reversal algo: {str(e)}")

    async def handle_menu_choice(self, choice: MenuOption) -> bool:
        handlers: Dict[MenuOption, Callable[[], Coroutine[Any, Any, Any] | bool]] = {
            MenuOption.CLOSE_TRADES: self.close_trades,
            MenuOption.FETCH_TRADES: self.fetch_trades,
            MenuOption.SCALE_IN_ALGO: self.run_scale_in_algo,
            MenuOption.REVERSAL_ALGO: self.run_reversal_algo,
            MenuOption.EXIT: lambda: False,
        }

        handler = handlers.get(choice)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler()
                return True
            return await handler()
        return True

    async def startup(self) -> bool:
        try:
            if not await connect_ib(self.ib):
                return False
            return True
        except Exception as e:
            logger.error(f"Error in startup: {str(e)}")

    async def shutdown(self) -> bool:
        try:
            disconnect_ib(self.ib)
        except Exception as e:
            logger.error("Shutdown error: {str(e)}")

    async def run(self):
        try:
            if not await self.startup():
                return

            while True:
                choice = await self.display_menu()
                if not choice:
                    continue

                should_continue = await self.handle_menu_choice(choice)
                if not should_continue:
                    break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
        finally:
            await self.shutdown()
