import pytest
from pydantic import BaseModel

from easyconfig.config_objs import ConfigObj
from easyconfig.errors import FunctionCallNotAllowedError


def test__repr__():
    class SimpleModel(BaseModel):
        a: int = 5

    o = ConfigObj(SimpleModel(), path=('__root__', 'child'))
    assert repr(o) == '<ConfigObj __root__.child>'


def test_forbidden_calls():
    class SimpleModel(BaseModel):
        a: int = 5

    o = ConfigObj(SimpleModel())

    with pytest.raises(FunctionCallNotAllowedError):
        o.parse_obj()

    with pytest.raises(FunctionCallNotAllowedError):
        o.parse_raw()

    with pytest.raises(FunctionCallNotAllowedError):
        o.parse_file()

    with pytest.raises(FunctionCallNotAllowedError) as e:
        o.from_orm()

    assert str(e.value) == 'Call "load_config_dict" or "load_config_file" on the app config instance!'


def test_attr_access():
    test_list = []

    class SimpleModel(BaseModel):
        a: int = 5

        def append(self):
            test_list.append(True)

    o = ConfigObj.from_model(SimpleModel())
    o.append()

    assert test_list == [True]
