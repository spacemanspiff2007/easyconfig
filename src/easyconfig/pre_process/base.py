from __future__ import annotations

from collections.abc import Callable, MutableMapping, MutableSequence
from typing import TYPE_CHECKING, Any, Final, TypeAlias, TypeVar

from easyconfig.yaml import CommentedMap, cmap_from_model


if TYPE_CHECKING:
    from pydantic import BaseModel


ContainingObj: TypeAlias = MutableSequence | MutableMapping

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

    def get_containing_obj(self, root: ContainingObj) -> ContainingObj | None:
        path = self.path

        if len(path) <= 1:
            return root

        obj = root

        try:
            for part in path[:-1]:
                obj = obj[part]
        except (KeyError, IndexError):
            return None

        if not isinstance(obj, (MutableSequence, MutableMapping)):
            return None

        return obj

    def ensure_valid_path(self, root: BaseModel) -> None:
        obj = root

        current_path = ()

        for path in self.path:
            current_path = current_path + (str(path), )

            if isinstance(obj, tuple):
                try:
                    obj = obj[path]
                except IndexError:
                    obj = None
            else:
                # we access the raw data through the aliases
                aliases = {
                    field.alias: name for name, field in obj.__class__.model_fields.items() if field.alias is not None
                }
                accessor = aliases.get(path, path)
                obj = getattr(obj, accessor, None)

            if obj is None:
                msg = f'Path "{".".join(current_path)}" does not exist in default'
                raise ValueError(msg)

    @staticmethod
    def _create_default(parent: ContainingObj, name: str | int, default: ContainingObj, path: tuple[str, ...]) -> None:
        if isinstance(parent, list):
            if not isinstance(name, int):
                msg = f'Expected int for list index, got {type(name)} at {".".join(path):s}'
                raise TypeError(msg)
            # we need to create a list with enough entries to access the current part
            while len(parent) <= name:
                parent.append({})

        if isinstance(default, list):
            parent[name] = []
        elif isinstance(default, dict):
            parent[name] = {}
        else:
            msg = f'Unsupported type {type(default)} at {".".join(path):s}'
            raise TypeError(msg) from None

    def get_containing_obj_or_create_default(self, root: ContainingObj,
                                             default: BaseModel | None = None) -> ContainingObj | None:
        if (dst_obj := self.get_containing_obj(root)) is not None:
            return dst_obj

        if default is None:
            return None

        default_yaml: CommentedMap | None = cmap_from_model(default)
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

                self._create_default(obj, part, default_yaml, current_path)
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
    def run(self, obj: ContainingObj, log_func: Callable[[str], Any] | None = None) -> None:
        raise NotImplementedError()

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    def check(self, default: BaseModel | None) -> None:
        raise NotImplementedError()
