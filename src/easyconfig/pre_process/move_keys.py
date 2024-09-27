from __future__ import annotations

from typing import TYPE_CHECKING, Final, Sized

from pydantic import BaseModel

from easyconfig.yaml import cmap_from_model

if TYPE_CHECKING:
    from logging import Logger


class PreProcessBase:
    def run(self, obj: dict):
        raise NotImplementedError()


class MoveKeyPreProcess(PreProcessBase):
    def __init__(self, src: tuple[str | int, ...], dst: tuple[str | int, ...],
                 logger: Logger | None = None, defaults: BaseModel | None = None):
        self.src: Final = src
        self.dst: Final = dst
        self.log: Final = logger
        self.defaults: Final = defaults

        # Validate the dst if we have a default so we catch e.g. typos
        if self.defaults is not None:
            yaml_defaults = cmap_from_model(self.defaults)
            if MoveKeyPreProcess._get_containing_obj(yaml_defaults, self.dst) is None:
                msg = f'Path "{".".join(self.dst[:-1]):s}" does not exist in default'
                raise ValueError(msg)

    def get_containing_dst_obj(self, obj: dict) -> dict | None:
        if (dst_obj := MoveKeyPreProcess._get_containing_obj(obj, self.dst)) is not None:
            return dst_obj

        if self.defaults is None:
            return None

        default_yaml = cmap_from_model(self.defaults)

        for part in self.dst[:-1]:
            if default_yaml is not None:
                try:
                    default_yaml = default_yaml[part]
                except (KeyError, IndexError):
                    default_yaml = None

            try:
                obj = obj[part]
            except (KeyError, IndexError):
                if default_yaml is None:
                    return None

                if isinstance(default_yaml, list):
                    obj[part] = []
                elif isinstance(default_yaml, dict):
                    obj[part] = {}
                else:
                    raise TypeError()
                obj = obj[part]

        return obj

    @staticmethod
    def _get_containing_obj(d: dict | Sized, path: tuple[str | int, ...]) -> dict | None:
        if not path:
            msg = 'Path with at least one entry expected'
            raise ValueError(msg)

        if len(path) <= 1:
            return d

        try:
            for part in path[:-1]:
                d = d[part]
        except (KeyError, IndexError):
            return None

        return d

    @staticmethod
    def _obj_exists(d: dict | Sized, path: tuple[str | int, ...]) -> bool:
        try:
            d[path[-1]]
        except (KeyError, IndexError):
            return False

        return True

    def run(self, obj: dict | list):
        if (src_obj := MoveKeyPreProcess._get_containing_obj(obj, self.src)) is None:
            return None

        if (dst_obj := self.get_containing_dst_obj(obj)) is None:
            return None

        # Never overwrite something
        if MoveKeyPreProcess._obj_exists(dst_obj, self.dst):
            return None

        # Source has to exist if we want to move to it
        if not MoveKeyPreProcess._obj_exists(src_obj, self.src):
            return None

        dst_obj[self.dst[-1]] = src_obj.pop(self.src[-1])
