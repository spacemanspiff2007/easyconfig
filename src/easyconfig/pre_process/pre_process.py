from collections.abc import Callable, MutableMapping, MutableSequence
from typing import Any, Final, TypeAlias

from pydantic import BaseModel
from typing_extensions import Self, override

from easyconfig.pre_process.base import PreProcessBase

from .delete_entry import DeleteEntryPreProcess
from .move_entry import MoveEntryPreProcess
from .rename_entry import RenameEntryPreProcess


PATH_INPUT_TYPE: TypeAlias = tuple[str | int, ...] | list[str | int]


def get_path_tuple(obj: PATH_INPUT_TYPE) -> tuple[str | int, ...]:
    if isinstance(obj, list):
        obj = tuple(obj)

    if not isinstance(obj, tuple):
        msg = f'Must be tuple or list, is {type(obj)}'
        raise TypeError(msg)

    for o in obj:
        if not isinstance(o, (str, int)):
            msg = f'Must be str or int, is {type(obj)}'
            raise TypeError(msg)
    return obj


class PreProcess(PreProcessBase):
    def __init__(self, default: BaseModel | None = None) -> None:
        self._operations: tuple[PreProcessBase, ...] = ()
        self._default: Final = default
        self._log: Callable[[str], Any] | None = None

    def _add(self, obj: PreProcessBase) -> None:
        for existing in self._operations:
            if existing == obj:
                msg = f'Operation {obj} already exists'
                raise ValueError(msg)
        self._operations += (obj,)

    def set_log_func(self, log_func: Callable[[str], Any] | None) -> Self:
        """Set a log function that will be called for each operation that is executed"""
        self._log = log_func
        return self

    def move_entry(self, src: PATH_INPUT_TYPE, dst: PATH_INPUT_TYPE) -> Self:
        """Move an entry to a different location in the configuration

        :param src: current path to the entry
        :param dst: new path to the entry
        :return:
        """
        self._add(MoveEntryPreProcess(get_path_tuple(src), get_path_tuple(dst), defaults=self._default))
        return self

    def rename_entry(self, src: PATH_INPUT_TYPE, name: str) -> Self:
        """Rename an entry in the configuration

        :param src: path to the entry
        :param name: new name
        """
        self._add(RenameEntryPreProcess(get_path_tuple(src), name))
        return self

    def delete_entry(self, path: PATH_INPUT_TYPE) -> Self:
        """Delete an entry in the configuration

        :param path: path to the entry
        """
        self._add(DeleteEntryPreProcess(get_path_tuple(path)))
        return self

    @override
    def run(self, obj: MutableSequence | MutableMapping, log_func: Callable[[str], Any] | None = None) -> None:
        if log_func is None:
            log_func = self._log

        for op in self._operations:
            op.run(obj, log_func)
