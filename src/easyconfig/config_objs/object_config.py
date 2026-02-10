from __future__ import annotations

from inspect import getmembers, isfunction
from typing import TYPE_CHECKING, Any, Final, NoReturn

from pydantic import BaseModel
from typing_extensions import Self

from easyconfig import AppConfigMixin
from easyconfig.__const__ import MISSING, MISSING_TYPE
from easyconfig.config_objs import ConfigNodeSubscriptionManager, ConfigObjSubscription
from easyconfig.errors import FunctionCallNotAllowedError


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from pydantic.fields import FieldInfo


def should_be_copied(o: object) -> bool:
    return isfunction(o) or isinstance(o, property)


NO_COPY = tuple(n for n, o in getmembers(AppConfigMixin) if should_be_copied(o))


class ConfigObj:
    def __init__(self, model: BaseModel, path: tuple[str, ...] = ('__root__',),
                 parent: MISSING_TYPE | ConfigObj = MISSING, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._obj_parent: Final = parent
        self._obj_path: Final = path

        self._obj_model_class: Final[type[BaseModel]] = model.__class__
        self._obj_model_fields: Final[dict[str, FieldInfo]] = model.__class__.model_fields
        self._obj_model_private_attrs: Final[tuple[str, ...]] = tuple(model.__private_attributes__.keys())

        self._obj_keys: tuple[str, ...] = ()
        self._obj_values: dict[str, Any] = {}
        self._obj_children: dict[str, ConfigObj | tuple[ConfigObj, ...]] = {}

        self._obj_subscriptions: ConfigNodeSubscriptionManager | None = None

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
                functions[name] = member  # noqa: PERF403

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

    def _set_values(self, obj: BaseModel, subscriptions: list[ConfigNodeSubscriptionManager]) -> bool:
        if not isinstance(obj, BaseModel):
            msg = f'Instance of {BaseModel.__class__.__name__} expected, got {obj} ({type(obj)})!'
            raise TypeError(msg)

        value_changed = False

        # Values of child objects
        for key, child in self._obj_children.items():
            value = getattr(obj, key, MISSING)
            if value is MISSING:
                continue

            if isinstance(child, tuple):
                for i, c in enumerate(child):
                    value_changed = c._set_values(value[i], subscriptions=subscriptions) or value_changed
            else:
                value_changed = child._set_values(value, subscriptions=subscriptions) or value_changed

        # Values of this object
        for key in self._obj_values:
            if (value := getattr(obj, key, MISSING)) is MISSING:
                continue

            old_value = self._obj_values.get(key, MISSING)
            self._obj_values[key] = value

            # Update only values, child objects change in place
            setattr(self, key, value)

            if old_value != value:
                value_changed = True

        # Notify subscribers
        if sub_manager := self._obj_subscriptions:
            return sub_manager.notify(value_changed, subscriptions)

        return value_changed

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self._full_obj_path}>'

    # ------------------------------------------------------------------------------------------------------------------
    # Match class signature with the Mixin Classes
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def config_file_path(self) -> Path:
        """Path to the loaded configuration file"""

        obj: ConfigObj | MISSING_TYPE = self
        while obj._obj_path != ('__root__',):
            obj = obj._obj_parent
            if obj is MISSING:
                msg = f'Parent object of {self._full_obj_path} is missing!'
                raise ValueError(msg)
        return obj.config_file_path

    def subscribe_set_options(self, *, propagate: bool | None = None, on_next_value: bool | None = None) -> Self:
        """Set options for the subscription of this object.

        :param propagate: Propagate the change event to the parent object
        :param on_next_value: Call the function the next time when values get loaded even if there is no value change
        """

        if self._obj_subscriptions is None:
            self._obj_subscriptions = ConfigNodeSubscriptionManager()

        self._obj_subscriptions.set_options(propagate=propagate, on_next_value=on_next_value)
        return self

    def subscribe_for_changes(self, func: Callable[[], Any]) -> ConfigObjSubscription:
        """When a value in this container changes the passed function will be called.

        :param func: function which will be called
        :return: object which can be used to cancel the subscription
        """

        if self._obj_subscriptions is None:
            self._obj_subscriptions = ConfigNodeSubscriptionManager()

        target_name = f'{func.__name__} @ {self._full_obj_path}'
        return self._obj_subscriptions.subscribe(func, target_name)

    # -----------------------------------------------------
    # pydantic 1
    @classmethod
    def parse_obj(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_raw(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_file(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def from_orm(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    # -----------------------------------------------------
    # pydantic 2
    @classmethod
    def model_validate_strings(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate_json(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()
