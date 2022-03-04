from json import loads
from typing import Any, Callable, Optional

from pydantic.fields import ModelField

import easyconfig
from easyconfig.__const__ import MISSING
from easyconfig.errors import ModelNotProperlyInitialized
from easyconfig.yaml import CommentedMap

from ._base import AccessBase


class ModelValueAccess(AccessBase):

    def set_from_model(self, model: 'easyconfig.ConfigModel',
                       transform: Optional[Callable[['ModelField', Any], Any]] = None) -> bool:

        # don't overwrite with model defaults once we have a value set
        # But set at least once so we transform the value
        if self._value_set:
            if self.name not in model.__fields_set__:
                return False
        self._value_set = True

        value = self.get_value()
        new = self.get_value(model)
        if transform is not None:
            new = transform(self.field, new)
        if new == value:
            return False
        setattr(self.model, self.name, new)
        return True

    def update_map(self, map: CommentedMap, use_file_defaults: bool) -> CommentedMap:
        key = self.yaml_key
        if key in map:
            return None

        value = self.get_default_value(use_file_defaults=use_file_defaults)
        if value is MISSING:
            raise ModelNotProperlyInitialized('Default value is missing')

        # don't add None to the yaml file because this will create empty entries
        # The same goes for list/dict
        if value is None:
            return None

        # YAML can't serialize all data types natively so we use the json serializer of the model
        # This works since a valid json is always a valid YAML
        _json_value = self.model.__config__.json_dumps(
            {'obj': value}, default=self.model.__json_encoder__)
        map[key] = loads(_json_value)['obj']

        self.add_comment_to_map(map)
        return None

    def add_comment_to_map(self, c_map: CommentedMap):
        if not self.yaml_description:
            return None

        key = self.yaml_key
        if key not in c_map.ca.items:
            c_map.yaml_add_eol_comment(self.field.field_info.description, key)
        return None
