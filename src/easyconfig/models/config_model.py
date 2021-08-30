from pydantic import BaseModel, PrivateAttr

import easyconfig.config_obj
from easyconfig.config_subscription import Subscription as _Subscription
from easyconfig.errors import FunctionCallNotAllowedError


class ConfigModel(BaseModel):
    _easyconfig: easyconfig.config_obj.EasyConfigObj = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._easyconfig = easyconfig.config_obj.EasyConfigObj(self)

    def on_all_values_set(self):
        """Override this function. It'll be called when all values from the file have been correctly set.
        Use it e.g. to calculate and set additional variables.
        """
        return None

    def subscribe_for_changes(self, func) -> _Subscription:
        """When a value in this container changes the passed function will be called.

        :param func: function which will be called
        :return: object which can be used to cancel the subscription
        """
        return self._easyconfig.subscribe(func)


    @classmethod
    def parse_obj(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError('Call "load_file" or "load_object" on the config instance!')

    @classmethod
    def parse_raw(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError('Call "load_file" or "load_object" on the config instance!')

    @classmethod
    def parse_file(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError('Call "load_file" or "load_object" on the config instance!')

    @classmethod
    def from_orm(cls, *args, **kwargs):
        raise FunctionCallNotAllowedError('Call "load_file" or "load_object" on the config instance!')
