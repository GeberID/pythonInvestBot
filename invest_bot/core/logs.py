import functools
import os
import sys
from datetime import datetime

from invest_bot.configs import LOGS_FOLDER, LOGS_FILENAME


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with open(LOGS_FILENAME, "a", encoding="utf-8") as log_file:
            result = None
            log_file.write(f'{datetime.now()} Trace: Command {func.__name__}() with parameters {args}, {kwargs}\n')
            try:
                result = func(*args, **kwargs)
                log_file.write(f'{datetime.now()} Trace: Command {func.__name__}() return -  {result!r}\n')
            except Exception as e:
                log_file.write(f'{datetime.now()} ERROR - {e.with_traceback(sys.exception().__traceback__)}\n')
            log_file.write("-------------------------------------------------------------------------\n")
        return result

    return wrapper


def create_logs_folder() -> None:
    try:
        os.mkdir(LOGS_FOLDER)
    except FileExistsError:
        print(f"Folder {LOGS_FOLDER} is exists")
