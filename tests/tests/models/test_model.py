from typing import List
from unittest.mock import Mock

from pydantic import Field

from easyconfig import ConfigModel


class SubModel(ConfigModel):
    s1 = 'sub1'
    l1: List[str] = ['asdf']


class MyTestModel(ConfigModel):
    p1: int = 0
    p2: float = 1.3

    sub: SubModel = Field(default_factory=SubModel)


def test_set_simple():
    cb = Mock()

    m1 = MyTestModel()
    m1._easyconfig_initialize().parse_model()
    m1._easyconfig.parent = 'root'
    m1.subscribe_for_changes(cb)

    cb.assert_not_called()
    assert m1.p1 == 0

    assert m1._easyconfig.set_values(MyTestModel(p1=1))

    cb.assert_called_once()
    assert m1.p1 == 1


def test_mutate_nested():
    m1 = MyTestModel()
    m1._easyconfig_initialize().parse_model()
    m2 = MyTestModel()
    m2._easyconfig_initialize().parse_model()

    sub1 = m1.sub

    m1._easyconfig.set_values(m2)

    assert m1.sub is sub1


def test_set_nested():
    cb = Mock()
    m1 = MyTestModel()
    m1._easyconfig_initialize().parse_model()
    m1._easyconfig.parent = 'root'

    m2 = MyTestModel()
    m2.sub.s1 = 'asdf'

    m1.subscribe_for_changes(cb)

    cb.assert_not_called()
    assert m1.sub.l1 == ['asdf']

    assert m1._easyconfig.set_values(m2)

    cb.assert_called_once()
    assert m1.sub.s1 == 'asdf'


def test_notify_first_load():
    cb = Mock()
    m1 = MyTestModel()
    m1._easyconfig_initialize().parse_model()
    m1._easyconfig.parent = 'root'

    m2 = MyTestModel()

    m1.subscribe_for_changes(cb)

    cb.assert_not_called()
    assert m1.p1 == 0

    m1._easyconfig.set_values(m2)
    cb.assert_called_once()
    assert m1.p1 == 0

    m1._easyconfig.set_values(m2)
    cb.assert_called_once()
    assert m1.p1 == 0
