from typing import Any, Callable


def default_exception_handler(e: Exception):
    raise e


HANDLER: Callable[[Exception], Any] = default_exception_handler


def set_exception_handler(handler: Callable[[Exception], Any]):
    global HANDLER
    HANDLER = handler


def process_exception(e: Exception):
    HANDLER(e)
