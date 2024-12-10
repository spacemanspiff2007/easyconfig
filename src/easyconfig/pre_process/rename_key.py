from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .base import PathAccessor, PreProcessBase


if TYPE_CHECKING:
    from logging import Logger


class RenameKeyPreProcess(PreProcessBase):
    def __init__(self, src: tuple[str | int, ...], new_name: str,
                 logger: Logger | None = None) -> None:
        self.src: Final = PathAccessor(src)
        self.dst: Final = PathAccessor(src[:-1] + (new_name,))
        self.log: Final = logger

    def run(self, obj: dict | list, logger: Logger | None = None) -> None:
        if (parent := self.src.get_containing_obj(obj)) is None:
            return None

        # Never overwrite something
        if self.dst.obj_exists(parent):
            return None

        # Source has to exist if we want to move to it
        if not self.src.obj_exists(parent):
            return None

        self.dst.set_obj(parent, self.src.pop_obj(parent))

        if logger is not None:
            logger.info(f'Entry "{self.src.key_name:s}" renamed to "{self.dst.key_name:s}" '
                        f'in "{self.src.containing_name}"')
