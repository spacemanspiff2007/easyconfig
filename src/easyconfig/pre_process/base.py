from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, MutableMapping, MutableSequence, TypeVar

from typing_extensions import NewType

from easyconfig.yaml import cmap_from_model


if TYPE_CHECKING:
    from pydantic import BaseModel


ContainingObj = NewType('ContainingObj', MutableSequence | MutableMapping)

A = TypeVar('A', bound=ContainingObj)


class PathAccessor:
    def __init__(self, path: tuple[str | int, ...]) -> None:
        if not path:
            msg = 'Path with at least one entry expected'
            raise ValueError(msg)

        self.path: Final = path

    @property
    def path_name(self) -> str:
        return '.'.join(str(part) for part in self.path)

    @property
    def containing_name(self) -> str:
        return '.'.join(str(part) for part in self.path[:-1])

    @property
    def key_name(self) -> str:
        return str(self.path[-1])

    def get_containing_obj(self, root: MutableSequence | MutableMapping) -> ContainingObj | None:
        path = self.path

        if len(path) <= 1:
            return root

        obj = root

        try:
            for part in path[:-1]:
                obj = obj[part]
        except (KeyError, IndexError):
            return None

        return obj

    def get_containing_obj_or_create_default(self, root: MutableSequence | MutableMapping,
                                             default: BaseModel | None = None) -> ContainingObj | None:
        if (dst_obj := self.get_containing_obj(root)) is not None:
            return dst_obj

        if default is None:
            return None

        default_yaml = cmap_from_model(default)
        obj = root

        current_path: tuple[str, ...] = ()
        for part in self.path[:-1]:
            current_path += (str(part),)

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
                    msg = f'Unsupported type {type(default_yaml)} at {".".join(current_path):s}'
                    raise TypeError(msg) from None
                obj = obj[part]

        return obj

    def obj_exists(self, containing_obj: ContainingObj) -> bool:
        try:
            containing_obj[self.path[-1]]
        except (KeyError, IndexError):
            return False

        return True

    def set_obj(self, containing_obj: A, value: Any) -> A:
        if self.obj_exists(containing_obj):
            msg = f'Object {self.path_name:s} already exists'
            raise ValueError(msg)

        containing_obj[self.path[-1]] = value
        return containing_obj

    def pop_obj(self, containing_obj: ContainingObj) -> Any:
        return containing_obj.pop(self.path[-1])

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.path_name:s}>'


class PreProcessBase:
    def run(self, obj: MutableSequence) -> None:
        raise NotImplementedError()
