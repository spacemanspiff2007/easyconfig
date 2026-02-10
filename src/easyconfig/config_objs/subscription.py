from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final, TypeAlias

from typing_extensions import Self

from easyconfig.errors import DuplicateSubscriptionError, SubscriptionAlreadyCanceledError


SubscriptionCallbackType: TypeAlias = Callable | Callable[[], Awaitable[Any]]


class ConfigNodeSubscriptionManager:
    def __init__(self) -> None:
        self._propagate: bool = False
        self._on_next_value: bool = False
        self._subscriptions: tuple[tuple[SubscriptionCallbackType, ConfigObjSubscription], ...] = ()

    def set_options(self, *, propagate: bool | None = None, on_next_value: bool | None = None) -> Self:
        if propagate is not None:
            self._propagate = propagate
        if on_next_value is not None:
            self._on_next_value = on_next_value
        return self

    def subscribe(self, cb: SubscriptionCallbackType, node_name: str) -> ConfigObjSubscription:
        for target, _ in self._subscriptions:
            if target is cb:
                msg = f'{cb} is already subscribed!'
                raise DuplicateSubscriptionError(msg)

        obj = ConfigObjSubscription(self, node_name)
        self._subscriptions += ((cb, obj), )
        return obj

    def cancel(self, subscription: ConfigObjSubscription) -> None:
        self._subscriptions = tuple((target, sub) for target, sub in self._subscriptions if sub is not subscription)
        return None

    def __bool__(self) -> bool:
        return bool(self._subscriptions)

    def notify(self, value_changed: bool, call_stack: list[ConfigNodeSubscriptionManager]) -> bool:  # noqa: FBT001
        if self._on_next_value:
            self._on_next_value = False
            call_stack.append(self)

        if value_changed:
            if self not in call_stack:
                call_stack.append(self)
            return self._propagate
        return False

    def call(self) -> None:
        for target, sub in self._subscriptions:
            result = target()
            if isinstance(result, Awaitable):
                msg = (f'Subscription target {target} @ {sub.name} is an async function! '
                       f'Use the async app config instead.')
                raise TypeError(msg)

    async def call_async(self) -> None:
        for target, _ in self._subscriptions:
            result = target()
            if isinstance(result, Awaitable):
                await result


class ConfigObjSubscription:
    def __init__(self, sub_obj: ConfigNodeSubscriptionManager, location: str) -> None:
        self._sub_manager: ConfigNodeSubscriptionManager | None = sub_obj
        self._sub_name: Final = location

    @property
    def name(self) -> str:
        """Location of the subscription target in the configuration"""
        return self._sub_name

    def cancel(self) -> None:
        """Cancel the subscription so that the function will no longer be called on changes"""
        parent = self._sub_manager
        self._sub_manager = None

        if parent is None:
            msg = f'Subscription for {self.name} was already canceled!'
            raise SubscriptionAlreadyCanceledError(msg)

        parent.cancel(self)

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} {self.name}>'
