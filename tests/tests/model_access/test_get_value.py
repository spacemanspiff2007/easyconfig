from typing import Tuple

from pydantic import BaseModel

from easyconfig import ConfigModel
from easyconfig.model_access import ModelModelAccess, ModelModelTupleAccess, ModelValueAccess


def test_value():

    class MyCfg(BaseModel):
        a: int = 7
        b: str = 'asdf'

    obj = MyCfg()
    a = ModelValueAccess('a', obj)

    assert obj.a == 7
    assert a.get_value() == 7

    a.set_from_model(MyCfg(a=9))

    assert obj.a == 9
    assert a.get_value() == 9


def test_model():

    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyCfg(BaseModel):
        a: int = 7
        b: MyEntryB = MyEntryB()

    obj = MyCfg()
    a = ModelModelAccess('b', obj)

    assert obj.b.b == 8.888
    assert a.get_value().b == 8.888
    obj.b.b = 77.77
    assert a.get_value().b == 77.77


def test_model_tuple():

    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyEntryC(ConfigModel):
        c: str = 'is_c'

    class MyCfg(BaseModel):
        a: Tuple[MyEntryB, MyEntryC] = (MyEntryB(), MyEntryC())

    obj = MyCfg()

    a = ModelModelTupleAccess('a', obj, 0)
    assert obj.a[0].b == 8.888
    assert a.get_value().b == 8.888

    a = ModelModelTupleAccess('a', obj, 1)
    assert obj.a[1].c == 'is_c'
    assert a.get_value().c == 'is_c'
