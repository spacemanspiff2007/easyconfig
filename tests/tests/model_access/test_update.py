from typing import Tuple

from pydantic import BaseModel

from easyconfig import ConfigModel
from easyconfig.model_access import ModelModelAccess, ModelModelTupleAccess, ModelValueAccess
from easyconfig.yaml import CommentedMap


def test_value():

    class MyCfg(BaseModel):
        a: int = 7
        b: str = 'asdf'

    obj = MyCfg()
    a = ModelValueAccess('a', obj)
    map = CommentedMap()

    a.update_map(map)
    assert map == {'a': 7}

    a.set_from_model(MyCfg(a=9))

    # the map value does not get overwritten
    a.update_map(map)
    assert map == {'a': 7}


def test_model():
    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyCfg(BaseModel):
        a: int = 7
        b: MyEntryB = MyEntryB()

    obj = MyCfg()
    a = ModelModelAccess('b', obj)
    map = CommentedMap()

    a.update_map(map)
    assert map == {'b': {}}


def test_model_tuple():

    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyEntryC(ConfigModel):
        c: str = 'is_c'

    class MyCfg(BaseModel):
        a: Tuple[MyEntryB, MyEntryC] = (MyEntryB(), MyEntryC())

    obj = MyCfg()
    a = ModelModelTupleAccess('a', obj, 1)
    map = CommentedMap()

    sub_map = a.update_map(map)
    assert map == {'a': [{}, {}]}
    assert map['a'][1] is sub_map
