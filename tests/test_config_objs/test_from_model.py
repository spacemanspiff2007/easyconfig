from typing import Tuple

from pydantic import BaseModel, PrivateAttr

from easyconfig.config_objs import ConfigObj
from easyconfig.models import ConfigMixin


def test_parse_values():
    class SimpleModel(BaseModel):
        a: int = 5
        b: int = 6

    o = ConfigObj.from_model(SimpleModel())
    assert o.a == 5
    assert o.b == 6


def test_parse_submodels():
    class SubModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    class SimpleModel(BaseModel, ConfigMixin):
        a: SubModel = SubModel()
        b: SubModel = SubModel(b=7)
        c: int = 3

    o = ConfigObj.from_model(SimpleModel())
    assert o._obj_values == {'c': 3}
    assert o.c == 3

    obj = o.a
    assert isinstance(obj, ConfigObj)
    assert obj.a == 5
    assert obj.b == 6
    assert obj._obj_path == ('__root__', 'a')

    obj = o.b
    assert isinstance(obj, ConfigObj)
    assert obj.a == 5
    assert obj.b == 7
    assert obj._obj_path == ('__root__', 'b')


def test_parse_submodel_tupels():
    class SubModel(BaseModel, ConfigMixin):
        a: int = 5

    class SimpleModel(BaseModel, ConfigMixin):
        a: Tuple[SubModel, SubModel] = (SubModel(), SubModel(a=7))
        c: int = 3

    o = ConfigObj.from_model(SimpleModel())
    assert o._obj_values == {'c': 3}

    obj = o.a[0]
    assert isinstance(obj, ConfigObj)
    assert obj.a == 5
    assert obj._obj_path == ('__root__', 'a', '0')

    obj = o.a[1]
    assert isinstance(obj, ConfigObj)
    assert obj.a == 7
    assert obj._obj_path == ('__root__', 'a', '1')


def test_func_call():
    class SimpleModel(BaseModel):
        a: int = 5
        b: int = 6

        def set_vars(self):
            self.a = 1
            self.b = 2
            return self.a + self.b

    o = ConfigObj.from_model(SimpleModel())
    assert o.a == 5
    assert o.b == 6

    o.set_vars()
    assert o.a == 1
    assert o.b == 2


def test_private_attr():
    class SimpleModel(BaseModel):
        a: int = 1
        _b: int = PrivateAttr()
        _c: int = PrivateAttr(3)

        def set_vars(self):
            self._b = 99

    o = ConfigObj.from_model(SimpleModel())
    assert o.a == 1
    assert not hasattr(o, '_b')
    assert o._c == 3

    o.set_vars()
    assert o._b == 99
