import functools
import inspect
import logging
import os
from typing import cast, TypeVar, Callable, Any

from investbot.configs import LOGS_FOLDER, LOGS_FILENAME

os.makedirs(LOGS_FOLDER, exist_ok=True)
logger = logging.getLogger("invest_bot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler(LOGS_FILENAME, encoding="utf-8")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

F = TypeVar("F", bound=Callable[..., Any])


def write_log(func: F) -> F:
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"RUNNING SYNC: {func.__name__} with parameters {args}, {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Command {func.__name__}() return -  {result!r}")
            return result
        except Exception:
            logger.exception(f"ERROR in SYNC {func.__name__}")
            raise

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"RUNNING ASYNC: {func.__name__} with parameters {args}, {kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Command {func.__name__}() return -  {result!r}")
            return result
        except Exception:
            logger.exception(f"ERROR in ASYNC {func.__name__}")
            raise

    if inspect.iscoroutinefunction(func):
        return cast(F, async_wrapper)
    return cast(F, sync_wrapper)


def create_logs_folder() -> None:
    if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)
