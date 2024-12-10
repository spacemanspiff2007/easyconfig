from __future__ import annotations

from collections.abc import Callable
from typing import Any, Final

from typing_extensions import override

from .base import PathAccessor, PreProcessBase


class DeleteEntryPreProcess(PreProcessBase):
    def __init__(self, src: tuple[str | int, ...]) -> None:
        self.dst: Final = PathAccessor(src)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeleteEntryPreProcess):
            return False
        return self.dst == other.dst

    @override
    def run(self, obj: dict | list, log_func: Callable[[str], Any] | None = None) -> None:
        if (parent := self.dst.get_containing_obj(obj)) is None:
            return None

        # If it doesn't exist we don't have to drop it
        if not self.dst.obj_exists(parent):
            return None

        self.dst.pop_obj(parent)

        if log_func is not None:
            log_func(f'Entry "{self.dst.path_name:s}" was deleted')
