import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from loguru import logger


class Logger:
    _logger = None  # Store the logger instance

    @staticmethod
    def get_logger():
        if Logger._logger is None:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)

            timezone = ZoneInfo("America/New_York")
            today = datetime.now(timezone).strftime("%Y-%m-%d")
            log_file = f"{log_dir}/{today}.log"

            # Remove default logger
            logger.remove()

            # Add file handler (all levels)
            logger.add(
                log_file,
                rotation="00:00",
                retention="7 days",
                format=(
                    "[{time:YYYY-MM-DD HH:mm:ss.SSS}] | "
                    "{level: <8} | "
                    "{message} | "
                    "{file}:{line}"
                ),
                level="DEBUG",
            )

            # Add console handler (INFO and above)
            logger.add(
                sink=sys.stderr,  # Use built-in stderr sink
                format=(
                    "<green>[{time:HH:mm:ss.SSS}]</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{message}</cyan> | "
                    "<yellow>{file}:{line}</yellow>"
                ),
                colorize=True,
                level="INFO",
            )

            Logger._logger = logger

        return Logger._logger

    @staticmethod
    def separator(text, level="INFO"):
        """
        Log a message with a separator line.
        :param text: Log message
        :param level: Log level (default is "INFO")
        """
        separator = "=" * 40
        logger.log(level, f"{text}\n{separator}")


# Example Usage
if __name__ == "__main__":
    log = Logger.get_logger()
    log.debug("Debug message (file only)")
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")
    log.separator("Section Break")
