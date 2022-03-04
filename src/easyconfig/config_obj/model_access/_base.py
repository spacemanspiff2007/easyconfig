from typing import Any, Callable, Optional, Tuple, Union

from pydantic import BaseModel
from pydantic.fields import ModelField

import easyconfig
from easyconfig.__const__ import CREATION_DEFAULT_KEY, MISSING, MISSING_TYPE
from easyconfig.errors.errors import InvalidFileValue


class AccessBase:
    def __init__(self, name: str, model: 'easyconfig.ConfigModel', path: Tuple[str, ...]):
        self.model: easyconfig.ConfigModel = model
        self.field: ModelField = model.__fields__[name]

        self.name: str = name           # Field / Variable name
        self.path: Tuple[str] = path    # Path to this entry

        self.default_field = MISSING
        self.default_file = MISSING
        self._value_set = False

    @property
    def yaml_key(self) -> str:
        return self.field.alias

    @property
    def yaml_description(self) -> Optional[str]:
        return self.field.field_info.description

    def get_default_value(self, use_file_defaults: bool):
        value = MISSING
        if use_file_defaults:
            value = self.default_file
        if value is MISSING:
            value = self.default_field
        return value

    def set_initial_values(self, default, field: ModelField, file_defaults=MISSING):
        self.default_field = default

        if file_defaults is not MISSING:
            file_value = self.get_value(file_defaults)
        else:
            file_value = field.field_info.extra.get(CREATION_DEFAULT_KEY, MISSING)
            if file_value is not MISSING:
                file_value, errors = field.validate(file_value, {}, loc='')
                if errors:
                    raise InvalidFileValue(
                        f'Value of {CREATION_DEFAULT_KEY} for {self.model.__class__.__name__}.{self.name} is invalid!'
                        f' Value: {file_value}'
                    )

        self.default_file = file_value

        # Check for unsupported keys
        unsupported_keys = set(field.field_info.extra.keys()) - {CREATION_DEFAULT_KEY}
        if unsupported_keys:
            raise ValueError(f'Unsupported keys {", ".join(unsupported_keys)} for '
                             f'{self.model.__class__.__name__}.{self.name}')

    def get_value(self, model: Union[BaseModel, dict, MISSING_TYPE] = MISSING) -> Any:
        if model is MISSING:
            return getattr(self.model, self.name)
        if isinstance(model, BaseModel):
            return getattr(model, self.name)
        if isinstance(model, dict):
            return model[self.name]
        raise ValueError()

    def __repr__(self):
        return f'<{self.__class__.__name__} {"->".join(self.path)} ({self.model.__class__.__name__}.{self.name})>'

    # Methods that need to be overridden
    def set_from_model(self, model: 'easyconfig.ConfigModel',
                       transform: Optional[Callable[['ModelField', Any], Any]] = None) -> bool:
        raise NotImplementedError()
