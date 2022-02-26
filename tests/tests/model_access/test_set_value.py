from typing import Tuple

from pydantic import BaseModel

from easyconfig import ConfigModel
from easyconfig.config_obj.model_access import ModelValueAccess


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

    # Setting from an object with defaults will not change the set values
    a.set_from_model(MyCfg())
    assert obj.a == 9
    assert a.get_value() == 9


def test_model_with_default_value():

    class MyEntryB(ConfigModel):
        opt: int = None

    class MyCfg(ConfigModel):
        b: MyEntryB = MyEntryB(opt=3)

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model()

    obj._easyconfig.set_values(MyCfg())
    assert obj.b.opt == 3

    obj._easyconfig.set_values(MyCfg(b=MyEntryB(opt=55)))
    assert obj.b.opt == 55

    obj._easyconfig.set_values(MyCfg(b=MyEntryB()))
    assert obj.b.opt == 55


def test_model_tuple():

    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyEntryC(ConfigModel):
        c: str = 'is_c'

    class MyCfg(ConfigModel):
        a: Tuple[MyEntryB, MyEntryC] = (MyEntryB(), MyEntryC())

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model()
    tuple_obj = obj.a

    obj._easyconfig.set_values(MyCfg())
    assert obj.a is tuple_obj
    assert obj.a[0].b == 8.888
    assert obj.a[1].c == 'is_c'

    obj._easyconfig.set_values(MyCfg(a=(MyEntryB(b=3.33), MyEntryC(c='c_new'))))
    assert obj.a is tuple_obj
    assert obj.a[0].b == 3.33
    assert obj.a[1].c == 'c_new'
