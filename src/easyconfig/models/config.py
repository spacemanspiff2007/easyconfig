from typing import TYPE_CHECKING, Any, Callable

from easyconfig.errors import FunctionCallNotAllowedError

if TYPE_CHECKING:
    import easyconfig
    import easyconfig.config_objs


class ConfigMixin:
    def subscribe_for_changes(
        self, func: Callable[[], Any], propagate: bool = False, on_next_load: bool = True
    ) -> 'easyconfig.config_objs.ConfigObjSubscription':
        """When a value in this container changes the passed function will be called.

        :param func: function which will be called
        :param propagate: Propagate the change event to the parent object
        :param on_next_load: Call the function the next time when values get loaded even if there is no value change
        :return: object which can be used to cancel the subscription
        """

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
