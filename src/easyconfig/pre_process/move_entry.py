from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from typing_extensions import override

from .base import PathAccessor, PreProcessBase


if TYPE_CHECKING:
    from collections.abc import Callable, MutableMapping, MutableSequence

    from pydantic import BaseModel


class MoveEntryPreProcess(PreProcessBase):
    def __init__(self, src: tuple[str | int, ...], dst: tuple[str | int, ...],
                 defaults: BaseModel | None = None) -> None:
        self.src: Final = PathAccessor(src)
        self.dst: Final = PathAccessor(dst)
        self.default: Final = defaults

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MoveEntryPreProcess):
            return False
        return self.src == other.src and self.dst == other.dst

    @override
    def run(self, obj: MutableSequence | MutableMapping, log_func: Callable[[str], Any] | None = None) -> None:
        if (src_obj := self.src.get_containing_obj(obj)) is None:
            return None

        if (dst_obj := self.dst.get_containing_obj_or_create_default(obj, self.default)) is None:
            return None

        # Never overwrite something
        if self.dst.obj_exists(dst_obj):
            return None

        # Source has to exist if we want to move to it
        if not self.src.obj_exists(src_obj):
            return None

        self.dst.set_obj(dst_obj, self.src.pop_obj(src_obj))

        if log_func is not None:
            log_func(f'Entry "{self.src.path_name:s}" moved to "{self.dst.path_name:s}"')
        return None

    @override
    def check(self, default: BaseModel | None) -> None:
        self.dst.ensure_valid_path(default)
