import functools
import time


def log_return_value(func):
    """
    Decorator that prints value returned by method
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper


def timeit(func):
    """
    Decorator that prints function execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} execution time: {end_time - start_time}")
        return result
    return wrapper
