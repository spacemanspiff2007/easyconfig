from typing import Any, Callable, Optional

import easyconfig
from easyconfig.__const__ import MISSING
from easyconfig.yaml import CommentedMap, CommentedSeq


class ModelValueAccess:
    def __init__(self, name: str, model: 'easyconfig.ConfigModel'):
        self.name: str = name
        self.model: easyconfig.ConfigModel = model

    def get_value(self, model=MISSING) -> Any:
        return getattr(self.model, self.name) if model is MISSING else getattr(model, self.name)

    def set_from_model(self, model: 'easyconfig.ConfigModel', transform: Optional[Callable[[Any], Any]] = None) -> bool:
        value = self.get_value()
        new = getattr(model, self.name)
        if transform is not None:
            new = transform(new)
        if new == value:
            return False
        setattr(self.model, self.name, new)
        return True

    def update_map(self, map: CommentedMap) -> CommentedMap:
        field_cfg = self.model.__fields__[self.name]
        key = field_cfg.alias

        if key in map:
            return None
        map[key] = self.get_value()

        if field_cfg.field_info.description is not None:
            if key not in map.ca.items:
                map.yaml_add_eol_comment(field_cfg.field_info.description, key)

        return None


class ModelModelAccess(ModelValueAccess):
    def get_value(self, model=MISSING) -> 'easyconfig.ConfigModel':
        return getattr(self.model, self.name) if model is MISSING else getattr(model, self.name)

    def set_from_model(self, model: 'easyconfig.ConfigModel') -> bool:
        raise NotImplementedError()

    def update_map(self, map: CommentedMap) -> CommentedMap:
        field_cfg = self.model.__fields__[self.name]
        key = field_cfg.alias

        if key in map:
            return map[key]
        map[key] = new_map = CommentedMap()

        if field_cfg.field_info.description is not None:
            if key not in map.ca.items:
                map.yaml_add_eol_comment(field_cfg.field_info.description, key)
        return new_map


class ModelModelTupleAccess(ModelModelAccess):
    def __init__(self, name: str, model: 'easyconfig.ConfigModel', pos: int):
        super().__init__(name=name, model=model)
        self.pos: int = pos

    def get_value(self, model=MISSING) -> 'easyconfig.ConfigModel':
        return getattr(self.model, self.name)[self.pos] if model is MISSING else getattr(model, self.name)[self.pos]

    def update_map(self, map: CommentedMap) -> CommentedMap:
        field_cfg = self.model.__fields__[self.name]
        key = field_cfg.alias

        # yaml doesn't know tuples, these entries are represented as lists
        if key in map:
            _list = map[key]
        else:
            map[key] = _list = CommentedSeq()

        while len(_list) <= self.pos:
            _list.append(CommentedMap())

        # the comment is on top
        if field_cfg.field_info.description is not None:
            if key not in map.ca.items:
                map.yaml_add_eol_comment(field_cfg.field_info.description, key)

        return _list[self.pos]
