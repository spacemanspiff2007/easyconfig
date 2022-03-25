from typing import Tuple

from pydantic import BaseModel

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
