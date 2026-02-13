import functools


def trace(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f'ТРАССИРОВКА: вызвана {func.__name__}() с {args}, {kwargs}')
        result = func(*args, **kwargs)
        print(f'ТРАССИРОВКА: {func.__name__}() вернула {result!r}\n')
        return result

    return wrapper
