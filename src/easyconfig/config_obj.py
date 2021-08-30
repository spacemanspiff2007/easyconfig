from enum import auto, Enum
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

import easyconfig
from easyconfig.config_subscription import Subscription
from easyconfig.errors import DuplicateSubscriptionError, ReferenceFolderMissingError
from easyconfig.errors.handler import process_exception
from easyconfig.model_access import ModelModelAccess, ModelModelTupleAccess, ModelValueAccess
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
        self.func_transform: Optional[Callable[[Any], Any]] = None

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

            # It's a tuple with models -> we don't replace those
            if isinstance(value, tuple) and all(map(lambda x: isinstance(x, easyconfig.ConfigModel), value)):
                for i, _value in enumerate(value):
                    self.model_models.append(ModelModelTupleAccess(name, self.model, i))
                continue

            self.model_values.append(ModelValueAccess(name, self.model))

        # Update parent for sub models
        for m_acc in self.model_models:
            cfg = m_acc.get_value()._easyconfig
            assert cfg.parent is PARENT_MISSING
            cfg.parent = self
            cfg.parse_model()
        return None

    def set_values(self, model: 'easyconfig.ConfigModel') -> bool:
        assert isinstance(model, self.model.__class__), f'{type(model)} != {type(self.model)}'

        changed = False
        for access in self.model_models:
            _model = access.get_value()
            changed = _model._easyconfig.set_values(access.get_value(model)) or changed
        for access in self.model_values:
            changed = access.set_from_model(model, self.func_transform) or changed

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

    def update_map(self, map: CommentedMap):
        for access in self.model_models:
            _map = access.update_map(map)
            access.get_value()._easyconfig.update_map(_map)
        for access in self.model_values:
            access.update_map(map)

    def get_base_path(self) -> Path:
        if self.base_path is not None:
            return self.base_path
        if self.parent is PARENT_ROOT or self.parent is PARENT_MISSING:
            raise ReferenceFolderMissingError()
        return self.parent.get_base_path()
