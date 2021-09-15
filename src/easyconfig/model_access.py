from json import loads
from typing import Any, Callable, Optional

from pydantic.fields import ModelField

import easyconfig
from easyconfig.__const__ import MISSING
from easyconfig.yaml import CommentedMap, CommentedSeq


class ModelValueAccess:
    def __init__(self, name: str, model: 'easyconfig.ConfigModel'):
        self.name: str = name
        self.model: easyconfig.ConfigModel = model
        self.field: ModelField = model.__fields__[name]

        self._val_set = False

    def get_value(self, model=MISSING) -> Any:
        return getattr(self.model, self.name) if model is MISSING else getattr(model, self.name)

    def set_from_model(self, model: 'easyconfig.ConfigModel',
                       transform: Optional[Callable[['ModelField', Any], Any]] = None) -> bool:

        # don't overwrite with model defaults once we have a value set
        # But set at least once so we transform the value
        if self._val_set:
            if self.name not in model.__fields_set__:
                return False
        self._val_set = True

        value = self.get_value()
        new = getattr(model, self.name)
        if transform is not None:
            new = transform(self.field, new)
        if new == value:
            return False
        setattr(self.model, self.name, new)
        return True

    def update_map(self, map: CommentedMap) -> CommentedMap:
        key = self.field.alias
        if key in map:
            return None

        # yaml can't serialize all data types natively so we use the json serializer of the model
        _json_value = self.model.__config__.json_dumps(
            {'obj': self.field.get_default()}, default=self.model.__json_encoder__)
        map[key] = loads(_json_value)['obj']

        self.add_comment_to_map(map)
        return None

    def add_comment_to_map(self, c_map: CommentedMap):
        if self.field.field_info.description is None:
            return None

        key = self.field.alias
        if key not in c_map.ca.items:
            c_map.yaml_add_eol_comment(self.field.field_info.description, key)
        return None


class ModelModelAccess(ModelValueAccess):
    def get_value(self, model=MISSING) -> 'easyconfig.ConfigModel':
        return getattr(self.model, self.name) if model is MISSING else getattr(model, self.name)

    def set_from_model(self, model: 'easyconfig.ConfigModel',
                       transform: Optional[Callable[['ModelField', Any], Any]] = None) -> bool:
        raise NotImplementedError()

    def update_map(self, map: CommentedMap) -> CommentedMap:
        key = self.field.alias
        if key in map:
            return map[key]
        map[key] = new_map = CommentedMap()

        self.add_comment_to_map(map)
        return new_map


class ModelModelTupleAccess(ModelModelAccess):
    def __init__(self, name: str, model: 'easyconfig.ConfigModel', pos: int):
        super().__init__(name=name, model=model)
        self.pos: int = pos

    def get_value(self, model=MISSING) -> 'easyconfig.ConfigModel':
        return getattr(self.model, self.name)[self.pos] if model is MISSING else getattr(model, self.name)[self.pos]

    def update_map(self, map: CommentedMap) -> CommentedMap:
        key = self.field.alias

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
