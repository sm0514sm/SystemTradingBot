import logging


class MethodLoggerDecorator:
    def __init__(self, f):
        self.func = f

    def __call__(self, *args, **kwargs):
        message = f"{self.func.__module__.split('.')[1]:>30}.py - {self.func.__name__:>20} " \
                  f"{self.func.__code__.co_firstlineno + 1:>3} | RUN"
        logging.getLogger("MethodLogger").debug(f'{message}, {args}, {kwargs}')
        self.func(self, *args, **kwargs)


def method_logger_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            message = f"{func.__module__.split('.')[0]:>30}.py - {func.__name__:>30} " \
                      f"{func.__code__.co_firstlineno + 1:>3} | RUN"
            logging.getLogger("MethodLogger").debug(f'{message}, {args[1:]}, {kwargs}')
        except Exception as e:
            logging.getLogger("MethodLogger").error(f'{e} 발생')
            pass
        return func(*args, **kwargs)

    return wrapper


def my_timer(original_function):
    import time

    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = original_function(*args, **kwargs)
        t2 = time.time() - t1
        logging.getLogger("MethodLogger").debug('{} 함수가 실행된 총 시간: {} 초'.format(original_function.__name__, t2))
        return result

    return wrapper
