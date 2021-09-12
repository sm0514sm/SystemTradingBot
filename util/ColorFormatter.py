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
    format = '%(asctime)s %(levelname)08s %(module)30s.py - %(funcName)20s %(lineno)3d | %(message)s'

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


if __name__ == "__main__":
    # create logger with 'spam_application'
    logger = logging.getLogger("SystemLogger")
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
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