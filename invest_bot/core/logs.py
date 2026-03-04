import functools
import os
from datetime import datetime

from invest_bot.configs import LOGS_FOLDER, LOGS_FILENAME


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with open(LOGS_FILENAME, "a", encoding="utf-8") as log_file:

            result = func(*args, **kwargs)
            log_file.write(f'{datetime.now()} Trace: Command {func.__name__}() with parameters {args}, {kwargs}\n')
            log_file.write(f'{datetime.now()} Trace: Command {func.__name__}() return -  {result!r}\n')
            log_file.write("-------------------------------------------------------------------------\n")
        return result

    return wrapper


def create_logs_folder():
    try:
        os.mkdir(LOGS_FOLDER)
    except FileExistsError:
        print("Папка уже существует, продолжаю работу")
