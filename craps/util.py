"""Provides utility functions."""

from functools import wraps
from time import perf_counter
from typing import Callable


def execution_time(
        func: Callable, *args,
        message: str = 'Execution of {name}() took {ms:.4f} ms', **kwargs,
) -> Callable:
    """Measures and prints the execution time of `func`. Use as a decorator.

    The message format string supports the following keywords:

        name: (str) Name of the function being measured.
        s: (float)  Execution time in seconds.
        ms: (float) Execution time in milliseconds.
        us: (float) Execution time in microseconds.

    Args:
        func: The function to measure.
        message: Message to print. Uses `str.format()`.

        Additional arguments are passed to `print()`.

    Returns:
        A decorated function that `print()`s its execution time.
    """
    @wraps(func)
    def wrapper(*w_args, **w_kwargs):
        start = perf_counter()
        result = func(*w_args, **w_kwargs)
        duration = perf_counter() - start

        output = message.format(
            name=func.__name__,
            s=duration, ms=duration * 1000, us=duration * 1000000,
        )
        print(output, *args, **kwargs)

        return result
    return wrapper
