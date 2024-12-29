import logging


class Logger:
    _logger = None

    @staticmethod
    def get_logger(name):
        if Logger._logger is None:
            # Create and configure logger
            Logger._logger = logging.getLogger(name)
            Logger._logger.setLevel(logging.INFO)

            # Create console handler and set level
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

            # Create formatter
            # "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(funcName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            ch.setFormatter(formatter)

            # Add handler to logger
            Logger._logger.addHandler(ch)

        return Logger._logger
