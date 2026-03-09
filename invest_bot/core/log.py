import functools
import os
import sys
from datetime import datetime
from typing import TypeVar, Callable, Any, cast

from invest_bot.configs import LOGS_FOLDER, LOGS_FILENAME

F = TypeVar("F", bound=Callable[..., Any])


def write_log(func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with open(LOGS_FILENAME, "a", encoding="utf-8") as log_file:
            result = None
            log_file.write(f"{datetime.now()} Trace: Command {func.__name__}() with parameters {args}, {kwargs}\n")
            try:
                result = func(*args, **kwargs)
                log_file.write(f"{datetime.now()} Trace: Command {func.__name__}() return -  {result!r}\n")
            except Exception as e:
                log_file.write(f"{datetime.now()} ERROR - {e.with_traceback(sys.exception().__traceback__)}\n")
                raise e
            log_file.write("-------------------------------------------------------------------------\n")
        return result

    return cast(F, wrapper)


def create_logs_folder() -> None:
    if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)
