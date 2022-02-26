from typing import Callable

import easyconfig
from easyconfig.errors import SubscriptionAlreadyCanceledError


class Subscription:
    def __init__(self, _cfg_obj: 'easyconfig.config_obj.EasyConfigObj', func: Callable):
        self._cfg_obj = _cfg_obj
        self._func = func

    def cancel(self):
        """Cancel the subscription so that the function will no longer be called on changes
        """
        if self._func not in self._cfg_obj.subs:
            raise SubscriptionAlreadyCanceledError(
                f'Subscription for "{getattr(self._func, "__name__", str(self._func))}" was already canceled')
        self._cfg_obj.subs.remove(self._func)
