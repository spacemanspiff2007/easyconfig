from typing import Tuple

from easyconfig import AppConfigModel, ConfigModel
from easyconfig.yaml import CommentedMap


def test_value():

    class MyCfg(AppConfigModel):
        a: int = 7
        b: str = 'asdf'

    obj = MyCfg()
    map = CommentedMap()

    obj._easyconfig.update_map(map)
    assert map == {'a': 7, 'b': 'asdf'}

    # Ensure the map value does not get overwritten
    # We always want to create the default
    obj._easyconfig.set_values(MyCfg(a=9))
    obj._easyconfig.update_map(map)
    assert map == {'a': 7, 'b': 'asdf'}


def test_model():
    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyCfg(AppConfigModel):
        a: int = 7
        b: MyEntryB = MyEntryB()

    obj = MyCfg()
    map = CommentedMap()

    obj._easyconfig.update_map(map)
    assert map == {'a': 7, 'b': {'b': 8.888}}

    # Ensure the map value does not get overwritten
    # We always want to create the default in the file
    obj._easyconfig.set_values(MyCfg(a=9))
    obj._easyconfig.update_map(map)
    assert map == {'a': 7, 'b': {'b': 8.888}}

    obj._easyconfig.set_values(MyCfg(a=9, b=MyEntryB(b=99)))
    obj._easyconfig.update_map(map)
    assert map == {'a': 7, 'b': {'b': 8.888}}


def test_model_tuple():

    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyEntryC(ConfigModel):
        c: str = 'is_c'

    class MyCfg(AppConfigModel):
        a: Tuple[MyEntryB, MyEntryC] = (MyEntryB(), MyEntryC())

    obj = MyCfg()
    map = CommentedMap()

    obj._easyconfig.update_map(map)
    assert map == {'a': [{'b': 8.888}, {'c': 'is_c'}]}

    # Ensure the map value does not get overwritten
    # We always want to create the default in the file
    obj._easyconfig.set_values(MyCfg())
    obj._easyconfig.update_map(map)
    assert map == {'a': [{'b': 8.888}, {'c': 'is_c'}]}

    obj._easyconfig.set_values(MyCfg(a=(MyEntryB(b=3.33), MyEntryC())))
    obj._easyconfig.update_map(map)
    assert map == {'a': [{'b': 8.888}, {'c': 'is_c'}]}
