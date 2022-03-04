from typing import Any, Callable, Optional, Tuple

from pydantic.fields import ModelField

import easyconfig
from easyconfig.__const__ import MISSING
from easyconfig.config_obj.model_access import ModelValueAccess
from easyconfig.yaml import CommentedMap, CommentedSeq


class ModelModelAccess(ModelValueAccess):
    def get_value(self, model=MISSING) -> 'easyconfig.ConfigModel':
        return super().get_value(model)

    def set_from_model(self, model: 'easyconfig.ConfigModel',
                       transform: Optional[Callable[['ModelField', Any], Any]] = None) -> bool:
        raise NotImplementedError()

    def update_map(self, map: CommentedMap, use_file_defaults: bool) -> CommentedMap:
        key = self.yaml_key
        if key in map:
            return map[key]
        map[key] = new_map = CommentedMap()

        # self.add_comment_to_map(map)
        self.add_comment_to_map(map)
        return new_map


class ModelModelTupleAccess(ModelModelAccess):
    def __init__(self, name: str, model: 'easyconfig.ConfigModel', path: Tuple[str, ...], pos: int):
        super().__init__(name=name, model=model, path=path)
        self.pos: int = pos

    def get_value(self, model=MISSING) -> 'easyconfig.ConfigModel':
        return super().get_value(model)[self.pos]

    def update_map(self, map: CommentedMap, use_file_defaults: bool) -> CommentedMap:
        key = self.yaml_key

        # yaml doesn't know tuples, these entries are represented as lists
        if key in map:
            _list = map[key]
        else:
            map[key] = _list = CommentedSeq()

        while len(_list) <= self.pos:
            _list.append(CommentedMap())

        # the comment is on top
        self.add_comment_to_map(map)
        return _list[self.pos]
