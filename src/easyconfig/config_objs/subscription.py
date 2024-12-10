from collections.abc import Callable
from typing import TYPE_CHECKING, Final

from easyconfig.errors import SubscriptionAlreadyCanceledError


if TYPE_CHECKING:
    import easyconfig


class SubscriptionParent:
    def __init__(
        self,
        func: Callable,
        cfg_obj: 'easyconfig.config_objs.HINT_CONFIG_OBJ',
        propagate: bool = False,
        on_next: bool = False,
    ) -> None:
        self.func: Callable | None = func
        self.cfg_obj: easyconfig.config_objs.HINT_CONFIG_OBJ | None = cfg_obj

        self.propagate: Final = propagate
        self.on_next: bool = on_next

    def notify(self, value_changed: bool) -> bool:
        if value_changed:
            self.on_next = False
            self.func()
            return self.propagate

        # Option to trigger the callback
        if self.on_next:
            self.on_next = False
            self.func()

        # don't propagate first load value
        return False

    def cancel(self) -> None:
        self.cfg_obj._obj_subscriptions.remove(self)
        self.func = None
        self.cfg_obj = None


class ConfigObjSubscription:
    def __init__(self, sub_obj: 'SubscriptionParent', target: str) -> None:
        self._sub_obj: SubscriptionParent | None = sub_obj
        self._sub_target: Final = target

    def cancel(self):
        """Cancel the subscription so that the function will no longer be called on changes"""
        parent = self._sub_obj
        self._sub_obj = None

        if parent is None:
            msg = f'Subscription for {self._sub_target} was already canceled!'
            raise SubscriptionAlreadyCanceledError(msg)
        parent.cancel()

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} {self._sub_target}>'
