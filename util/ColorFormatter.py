import logging


class ColorFormatter(logging.Formatter):
    grey = "\033[37m"
    white = "\033[97m"
    green = "\033[92m"
    blue = "\033[94m"
    yellow = "\033[93m"
    red = "\033[91m"
    rred = "\033[31m"
    reset = "\033[0m"
    format = '%(asctime)s %(levelname)08s %(module)30s.py - %(funcName)30s %(lineno)3d | %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: white + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: rred + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class FileLoggerFormatter(logging.Formatter):
    format = '%(asctime)s %(levelname)08s %(message)s'

    FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class MethodLoggerFormatter(logging.Formatter):
    grey = "\033[37m"
    white = "\033[97m"
    green = "\033[92m"
    blue = "\033[94m"
    yellow = "\033[93m"
    red = "\033[91m"
    rred = "\033[31m"
    reset = "\033[0m"
    format = '%(asctime)s %(levelname)08s %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: white + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: rred + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class CoinInfoLoggerFormatter(logging.Formatter):
    grey = "\033[37m"
    white = "\033[97m"
    green = "\033[92m"
    blue = "\033[94m"
    yellow = "\033[93m"
    red = "\033[91m"
    rred = "\033[31m"
    reset = "\033[0m"
    format = '%(asctime)s | %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: white + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: rred + format + reset
    }

    def format(self, record):
        fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


if __name__ == "__main__":
    logger = logging.getLogger("SystemLogger")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColorFormatter())
    logger.addHandler(ch)

    print("하얀색")
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")

    # -------------------------------------
    coin_logger = logging.getLogger("CoinInfoLogger")
    coin_logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CoinInfoLoggerFormatter())
    coin_logger.addHandler(ch)

    print("하얀색")
    coin_logger.debug("debug message")
    coin_logger.info("info message")
    coin_logger.warning("warning message")
    coin_logger.error("error message")
    coin_logger.critical("critical message")
