from __future__ import annotations

from inspect import getmembers, isfunction
from typing import TYPE_CHECKING, Any, Final

from pydantic import BaseModel
from typing_extensions import Self

from easyconfig import AppConfigMixin
from easyconfig.__const__ import MISSING, MISSING_TYPE
from easyconfig.config_objs import ConfigObjSubscription, SubscriptionParent
from easyconfig.errors import DuplicateSubscriptionError, FunctionCallNotAllowedError


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from pydantic.fields import FieldInfo


def should_be_copied(o: object) -> bool:
    return isfunction(o) or isinstance(o, property)


NO_COPY = tuple(n for n, o in getmembers(AppConfigMixin) if should_be_copied(o))


class ConfigObj:
    def __init__(self, model: BaseModel, path: tuple[str, ...] = ('__root__',),
                 parent: MISSING_TYPE | ConfigObj = MISSING, **kwargs) -> None:
        super().__init__(**kwargs)

        self._obj_parent: Final = parent
        self._obj_path: Final = path

        self._obj_model_class: Final = model.__class__
        self._obj_model_fields: dict[str, FieldInfo] = model.model_fields
        self._obj_model_private_attrs: list[str] = list(model.__private_attributes__.keys())

        self._obj_keys: tuple[str, ...] = ()
        self._obj_values: dict[str, Any] = {}
        self._obj_children: dict[str, ConfigObj | tuple[ConfigObj, ...]] = {}

        self._obj_subscriptions: list[SubscriptionParent] = []

        self._last_model: BaseModel = model

    @property
    def _full_obj_path(self) -> str:
        return '.'.join(self._obj_path)

    @classmethod
    def from_model(cls, model: BaseModel, path: tuple[str, ...] = ('__root__',),
                   parent: MISSING_TYPE | ConfigObj = MISSING, **kwargs) -> Self:

        # Copy functions from the class definition to the child class
        functions = {}
        for name, member in getmembers(model.__class__):
            if not name.startswith('_') and name not in NO_COPY and should_be_copied(member):
                functions[name] = member

        # Create a new class that pulls down the user defined functions if there are any
        # It's not possible to attach the functions to the existing class instance
        if functions:
            new_cls = type(f'{model.__class__.__name__}{cls.__name__}', (cls,), functions)
            ret = new_cls(model, path, parent, **kwargs)
        else:
            ret = cls(model, path, parent, **kwargs)

        # Set the values or create corresponding subclasses
        keys = []
        for key in ret._obj_model_fields:
            value = getattr(model, key, MISSING)
            if value is MISSING:
                continue

            keys.append(key)

            if isinstance(value, BaseModel):
                ret._obj_children[key] = attrib = ConfigObj.from_model(value, path=(*path, key), parent=ret)
            elif isinstance(value, tuple) and all(isinstance(x, BaseModel) for x in value):
                ret._obj_children[key] = attrib = tuple(
                    ConfigObj.from_model(o, path=(*path, key, str(i)), parent=ret) for i, o in enumerate(value)
                )
            else:
                ret._obj_values[key] = attrib = value

            # set child and values
            setattr(ret, key, attrib)

        # copy private attributes - these are the same as values
        for key in ret._obj_model_private_attrs:
            value = getattr(model, key, MISSING)
            if value is MISSING:
                continue

            keys.append(key)

            ret._obj_values[key] = value
            setattr(ret, key, value)

        ret._obj_keys = tuple(keys)
        return ret

    def _set_values(self, obj: BaseModel) -> bool:
        if not isinstance(obj, BaseModel):
            msg = f'Instance of {BaseModel.__class__.__name__} expected, got {obj} ({type(obj)})!'
            raise TypeError(msg)

        # Update last model so we can delegate function calls
        self._last_model = obj

        value_changed = False

        # Values of child objects
        for key, child in self._obj_children.items():
            value = getattr(obj, key, MISSING)
            if value is MISSING:
                continue

            if isinstance(child, tuple):
                for i, c in enumerate(child):
                    value_changed = c._set_values(value[i]) or value_changed
            else:
                value_changed = child._set_values(value) or value_changed

        # Values of this object
        for key in self._obj_values:
            value = getattr(obj, key, MISSING)
            if value is MISSING:
                continue
            old_value = self._obj_values.get(key, MISSING)
            self._obj_values[key] = value

            # Update only values, child objects change in place
            setattr(self, key, value)

            if old_value != value:
                value_changed = True

        # Notify subscribers
        propagate = False if self._obj_subscriptions else value_changed
        for sub in self._obj_subscriptions:
            propagate = sub.notify(value_changed) or propagate

        return propagate

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self._full_obj_path}>'

    # def __getattr__(self, item):
    #     # delegate call to model
    #     return getattr(self._last_model, item)

    # ------------------------------------------------------------------------------------------------------------------
    # Match class signature with the Mixin Classes
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def loaded_file_path(self) -> Path:
        """Path to the loaded configuration file"""

        obj = self
        while obj._obj_path != ('__root__',):
            obj = obj._obj_parent
        return obj.loaded_file_path

    def subscribe_for_changes(self, func: Callable[[], Any], *,
                              propagate: bool = False, on_next_load: bool = True) -> ConfigObjSubscription:
        """When a value in this container changes the passed function will be called.

        :param func: function which will be called
        :param propagate: Propagate the change event to the parent object
        :param on_next_load: Call the function the next time when values get loaded even if there is no value change
        :return: object which can be used to cancel the subscription
        """

        target = f'{func.__name__} @ {self._full_obj_path}'
        for sub in self._obj_subscriptions:
            if sub.func is func:
                msg = f'{target} is already subscribed!'
                raise DuplicateSubscriptionError(msg)

        sub = SubscriptionParent(func, self, propagate=propagate, on_next=on_next_load)
        self._obj_subscriptions.append(sub)
        return ConfigObjSubscription(sub, target)

    # -----------------------------------------------------
    # pydantic 1
    @classmethod
    def parse_obj(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_raw(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_file(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def from_orm(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    # -----------------------------------------------------
    # pydantic 2
    @classmethod
    def model_validate_strings(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate_json(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()
