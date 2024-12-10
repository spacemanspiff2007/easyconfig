from __future__ import annotations

from typing import TYPE_CHECKING, Final

from easyconfig.yaml import cmap_from_model

from .base import PathAccessor, PreProcessBase


if TYPE_CHECKING:
    from logging import Logger

    from pydantic import BaseModel


class MoveKeyPreProcess(PreProcessBase):
    def __init__(self, src: tuple[str | int, ...], dst: tuple[str | int, ...],
                 logger: Logger | None = None, defaults: BaseModel | None = None) -> None:
        self.src: Final = PathAccessor(src)
        self.dst: Final = PathAccessor(dst)
        self.log: Final = logger
        self.default: Final = defaults

        # Validate the dst if we have a default so we catch e.g. typos
        if self.default is not None:
            yaml_defaults = cmap_from_model(self.default)
            if self.dst.get_containing_obj(yaml_defaults) is None:
                msg = f'Path "{self.dst.containing_name}" does not exist in default'
                raise ValueError(msg)

    def run(self, obj: dict | list, logger: Logger | None = None) -> None:
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

        if logger is not None:
            logger.info(f'Configuration "{self.src.path_name:s}" moved to "{self.dst.path_name:s}"')
