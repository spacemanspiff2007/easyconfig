from collections.abc import Callable
from typing import Any


def default_exception_handler(e: Exception):
    raise e


HANDLER: Callable[[Exception], Any] = default_exception_handler


def set_exception_handler(handler: Callable[[Exception], Any]) -> None:
    global HANDLER
    HANDLER = handler


def process_exception(e: Exception) -> None:
    HANDLER(e)
