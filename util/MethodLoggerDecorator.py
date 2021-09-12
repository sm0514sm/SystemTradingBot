import logging


class MethodLoggerDecorator:

    def __init__(self, f):
        self.func = f
        self.method_logger = logging.getLogger("MethodLogger")

    def __call__(self, *args, **kwargs):
        message = f"{self.func.__module__.split('.')[1]:>30}.py - {self.func.__name__:>20} " \
                  f"{self.func.__code__.co_firstlineno + 1:>3} | RUN"
        self.method_logger.debug(f'{message}, {args}, {kwargs}')
        self.func(self, *args, **kwargs)


