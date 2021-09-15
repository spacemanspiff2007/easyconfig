from enum import auto, Enum
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

from pydantic.fields import ModelField

import easyconfig
from easyconfig.errors import DuplicateSubscriptionError, ReferenceFolderMissingError
from easyconfig.errors.handler import process_exception
from easyconfig.model_access import ModelModelAccess, ModelModelTupleAccess, ModelValueAccess
from easyconfig.model_subscription import Subscription
from easyconfig.yaml import CommentedMap


class _ParentType(Enum):
    MISSING = auto()
    ROOT = auto()


PARENT_ROOT = _ParentType.ROOT
PARENT_MISSING = _ParentType.MISSING


class EasyConfigObj:
    def __init__(self, model: 'easyconfig.ConfigModel'):
        self.model: easyconfig.ConfigModel = model
        self.parent: Union[EasyConfigObj, _ParentType] = PARENT_MISSING

        self.subs: List[Callable] = []

        self.base_path: Optional[Path] = None
        self.func_transform: Optional[Callable[[ModelField, Any], Any]] = None

        self.first_set = True

        # User defined models/structure
        self.model_models: List[ModelModelAccess] = []
        self.model_values: List[ModelValueAccess] = []

    def subscribe(self, func: Callable) -> Subscription:
        assert callable(func)

        # assert that it's not a detached obj
        assert self.parent is not PARENT_MISSING

        if func in self.subs:
            raise DuplicateSubscriptionError(f'Func "{getattr(func, "__name__", str(func))}" is already subscribed')

        self.subs.append(func)
        return Subscription(self, func)

    def notify(self):
        for f in self.subs:
            try:
                f()
            except Exception as e:
                process_exception(e)

    def parse_model(self):
        for name in self.model.__fields__:
            value = getattr(self.model, name)

            if isinstance(value, easyconfig.ConfigModel):
                self.model_models.append(ModelModelAccess(name, self.model))
                continue

            # It's a tuple with models -> we don't replace those instead we mutate the values
            if isinstance(value, tuple) and all(map(lambda x: isinstance(x, easyconfig.ConfigModel), value)):
                for i, _value in enumerate(value):  # type: int, easyconfig.ConfigModel
                    self.model_models.append(ModelModelTupleAccess(name, self.model, i))
                continue

            self.model_values.append(ModelValueAccess(name, self.model))

        # Update parent for sub models
        for m_acc in self.model_models:
            dst_model = m_acc.get_value()
            # since we validated the defaults we have a (validated) copy of the sub model instance.
            # That's why we  initialize the config only here and not earlier (e.g. in __init__ of the model)
            cfg = dst_model._easyconfig_initialize()

            # Build a tree so we can get values from the parent
            assert cfg.parent is PARENT_MISSING
            cfg.parent = self
            cfg.parse_model()
        return None

    def set_values(self, model: 'easyconfig.ConfigModel') -> bool:
        assert isinstance(model, self.model.__class__), f'{type(model)} != {type(self.model)}'

        changed = False
        for m_access in self.model_models:
            modify_model = m_access.get_value()
            changed = modify_model._easyconfig.set_values(m_access.get_value(model)) or changed
        for v_access in self.model_values:
            changed = v_access.set_from_model(model, self.func_transform) or changed

        # callback when all values are set
        try:
            self.model.on_all_values_set()
        except Exception as e:
            process_exception(e)

        # Notify listeners after we have processed the content
        if changed or self.first_set:
            self.first_set = False
            self.notify()
        return changed

    def update_map(self, c_map: CommentedMap):
        for m_access in self.model_models:
            _map = m_access.update_map(c_map)
            m_access.get_value()._easyconfig.update_map(_map)
        for v_access in self.model_values:
            v_access.update_map(c_map)

    def get_base_path(self) -> Path:
        if self.base_path is not None:
            return self.base_path
        if not isinstance(self.parent, EasyConfigObj):
            raise ReferenceFolderMissingError(f'Parent is {self.parent}')
        return self.parent.get_base_path()
