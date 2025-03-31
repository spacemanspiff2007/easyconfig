from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from easyconfig.errors import SubscriptionAlreadyCanceledError


if TYPE_CHECKING:
    from collections.abc import Callable


class SubscriptionParent:
    def __init__(self, func: Callable, cancel_func: Callable[[SubscriptionParent], Any], *,
                 propagate: bool = False, on_next: bool = False) -> None:
        self.func: Callable | None = func
        self.cancel_func: Callable[[SubscriptionParent], Any] | None = cancel_func

        self.propagate: Final = propagate
        self.on_next: bool = on_next

    def notify(self, value_changed: bool) -> bool:  # noqa: FBT001
        # Already canceled - should never happen
        if self.func is None or self.cancel_func is None:
            return True

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
        cancel_func = self.cancel_func
        self.cancel_func = None
        self.func = None

        if cancel_func is not None:
            cancel_func(self)
        return None


class ConfigObjSubscription:
    def __init__(self, sub_obj: SubscriptionParent, target: str) -> None:
        self._sub_obj: SubscriptionParent | None = sub_obj
        self._sub_target: Final = target

    def cancel(self) -> None:
        """Cancel the subscription so that the function will no longer be called on changes"""
        parent = self._sub_obj
        self._sub_obj = None

        if parent is None:
            msg = f'Subscription for {self._sub_target} was already canceled!'
            raise SubscriptionAlreadyCanceledError(msg)

        parent.cancel()

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} {self._sub_target}>'
