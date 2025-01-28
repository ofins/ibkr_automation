from loguru import logger


class Logger:
    _logger_initialized = False  # Track if the logger is already initialized

    @staticmethod
    def get_logger():
        if not Logger._logger_initialized:
            # Remove default logger and configure a custom one
            logger.remove()  # Remove default logger
            logger.add(
                sink=lambda msg: print(f"{msg}", end=""),  # Output to console
                format=(
                    "<green>[{time:HH:mm:ss.SSS}]</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{message}</cyan> | "
                ),
                colorize=True,
            )

            logger.add(
                sink=lambda msg: print(f"{msg}", end=""),  # Output to console
                format=(
                    "<green>[{time:HH:mm:ss.SSS}]</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{message}</cyan> | "
                    "<yellow>{file}:{line}</yellow>"
                ),
                colorize=True,
                level="ERROR",  # Only for error messages
            )

            Logger._logger_initialized = True  # Mark as initialized

        return logger

    @staticmethod
    def separator(text, level="INFO"):
        """
        Log a message with a separator line.
        :param emoji: Emoji to prefix the log message
        :param text: Log message
        :param level: Log level (default is "INFO")
        """
        separator = "=" * 40
        logger.log(level, f"{text}")
        print(separator)


# Example Usage
if __name__ == "__main__":
    log = Logger.get_logger()
    # log.info("This is a standard log message.")

# Logging emoji guide
# Emoji	Description
# 🟢	Connected
# ⛔	   Disconnected
# ⚠️    Error
# 🚫    Closed positions
# 🔃    Updated positions
# 🔺    Buy
# 🔻    Sell
# 📈    Report
