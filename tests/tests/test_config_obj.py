from unittest.mock import Mock

import pytest

import easyconfig
from easyconfig.config_obj import EasyConfigObj
from easyconfig.errors import DuplicateSubscriptionError, SubscriptionAlreadyCanceledError


def test_subscribe():
    obj = EasyConfigObj(None)
    obj.parent = 'parent'

    def test_func():
        pass

    sub = obj.subscribe(test_func)

    # test subscribe multiple times
    with pytest.raises(DuplicateSubscriptionError) as e:
        obj.subscribe(test_func)
    assert str(e.value) == 'Func "test_func" is already subscribed'

    # test remove
    assert test_func in obj.subs
    sub.cancel()
    assert test_func not in obj.subs

    # test unsubscribe multiple times
    with pytest.raises(SubscriptionAlreadyCanceledError) as e:
        sub.cancel()
    assert str(e.value) == 'Subscription for "test_func" was already canceled'


def test_call():
    obj = EasyConfigObj(None)
    obj.parent = 'parent'
    m = Mock()

    obj.subscribe(m)

    m.assert_not_called()
    obj.notify()
    m.assert_called_once()


def test_call_err(monkeypatch):
    handler = Mock()
    monkeypatch.setattr(easyconfig.errors.handler, 'HANDLER', handler)

    err = ValueError('exception')

    obj = EasyConfigObj(None)
    obj.parent = 'parent'
    m1 = Mock(side_effect=err)
    m2 = Mock()

    obj.subscribe(m1)
    obj.subscribe(m2)

    handler.assert_not_called()
    m1.assert_not_called()
    m2.assert_not_called()

    obj.notify()

    m1.assert_called_once()
    m2.assert_called_once()
    handler.assert_called_once_with(err)
