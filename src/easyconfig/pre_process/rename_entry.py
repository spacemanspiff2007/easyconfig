from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from typing_extensions import override

from .base import ContainingObj, PathAccessor, PreProcessBase


if TYPE_CHECKING:
    from collections.abc import Callable


class RenameEntryPreProcess(PreProcessBase):
    def __init__(self, src: tuple[str | int, ...], new_name: str) -> None:
        self.src: Final = PathAccessor(src)
        self.dst: Final = PathAccessor(src[:-1] + (new_name,))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RenameEntryPreProcess):
            return False
        return self.src == other.src and self.dst == other.dst

    @override
    def run(self, obj: ContainingObj, log_func: Callable[[str], Any] | None = None) -> None:
        if (parent := self.src.get_containing_obj(obj)) is None:
            return None

        # Never overwrite something
        if self.dst.obj_exists(parent):
            return None

        # Source has to exist if we want to move to it
        if not self.src.obj_exists(parent):
            return None

        self.dst.set_obj(parent, self.src.pop_obj(parent))

        if log_func is not None:
            c_name = self.src.containing_name
            loc = f' in "{c_name}"' if c_name else ''
            log_func(f'Entry "{self.src.key_name:s}" renamed to "{self.dst.key_name:s}"{loc:s}')

        return None
