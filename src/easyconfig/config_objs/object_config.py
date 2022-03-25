from typing import Any, Callable, Dict, List, Tuple, Type, TYPE_CHECKING, TypeVar, Union

from pydantic import BaseModel
from pydantic.fields import ModelField
from typing_extensions import Final

from easyconfig.__const__ import MISSING, MISSING_TYPE
from easyconfig.config_objs import ConfigObjSubscription, SubscriptionParent
from easyconfig.errors import DuplicateSubscriptionError, FunctionCallNotAllowedError

if TYPE_CHECKING:
    import easyconfig


HINT_CONFIG_OBJ = TypeVar('HINT_CONFIG_OBJ', bound='ConfigObj')
HINT_CONFIG_OBJ_TYPE = Type[HINT_CONFIG_OBJ]


class ConfigObj:
    def __init__(self, model: BaseModel,
                 path: Tuple[str, ...] = ('__root__', ),
                 parent: Union[MISSING_TYPE, HINT_CONFIG_OBJ] = MISSING):

        self._obj_parent: Final = parent
        self._obj_path: Final = path

        self._obj_model_fields: Dict[str, ModelField] = model.__fields__
        self._obj_model_class: Final = model.__class__

        self._obj_keys: Tuple[str, ...] = tuple()
        self._obj_values: Dict[str, Any] = {}
        self._obj_children: Dict[str, Union[HINT_CONFIG_OBJ, Tuple[HINT_CONFIG_OBJ, ...]]] = {}

        self._obj_subscriptions: List[SubscriptionParent] = []

        self._last_model: BaseModel = model

    @classmethod
    def from_model(cls, model: BaseModel,
                   path: Tuple[str, ...] = ('__root__', ),
                   parent: Union[MISSING_TYPE, HINT_CONFIG_OBJ] = MISSING):

        ret = cls(model, path, parent)

        keys = []
        for key in ret._obj_model_fields.keys():
            value = getattr(model, key, MISSING)
            if value is MISSING:
                continue

            keys.append(key)

            if isinstance(value, BaseModel):
                ret._obj_children[key] = attrib = cls.from_model(value, path=path + (key,), parent=ret)
            elif isinstance(value, tuple) and all(map(lambda x: isinstance(x, BaseModel), value)):
                ret._obj_children[key] = attrib = tuple(
                    cls.from_model(o, path=path + (key, str(i)), parent=ret) for i, o in enumerate(value)
                )
            else:
                ret._obj_values[key] = attrib = value

            # set child and values
            setattr(ret, key, attrib)

        ret._obj_keys = tuple(keys)
        return ret

    def _set_values(self, obj: BaseModel) -> bool:
        if not isinstance(obj, BaseModel):
            raise ValueError(f'Instance of {BaseModel.__class__.__name__} expected, got {obj} ({type(obj)})!')

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
            old_value = self._obj_values[key]
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

    def __repr__(self):
        return f'<{self.__class__.__name__} {".".join(self._obj_path)}>'

    def __getattr__(self, item):
        # delegate call to model
        return getattr(self._last_model, item)

    # ------------------------------------------------------------------------------------------------------------------
    # Match class signature with the Mixin Classes
    # ------------------------------------------------------------------------------------------------------------------
    def subscribe_for_changes(self, func: Callable[[], Any], propagate: bool = False, on_next_load: bool = True) \
            -> 'easyconfig.config_objs.ConfigObjSubscription':

        target = f'{func.__name__} @ {".".join(self._obj_path)}'
        for sub in self._obj_subscriptions:
            if sub.func is func:
                raise DuplicateSubscriptionError(f'{target} is already subscribed!')

        sub = SubscriptionParent(func, self, propagate=propagate, on_next=on_next_load)
        self._obj_subscriptions.append(sub)
        return ConfigObjSubscription(sub, target)

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_raw(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_file(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError()

    @classmethod
    def from_orm(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError()
