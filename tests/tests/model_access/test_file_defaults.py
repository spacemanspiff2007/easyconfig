from typing import Dict, Optional

import pytest
from pydantic import Field

from easyconfig import ConfigModel
from easyconfig.__const__ import MISSING
from easyconfig.errors import InvalidFileValue


def test_invalid_value():

    class MyCfg(ConfigModel):
        a: int = Field(7, file_value='asdf')
        b: str = 'asdf'

    obj = MyCfg()

    with pytest.raises(InvalidFileValue) as e:
        obj._easyconfig_initialize().parse_model(set_default_value=True)

    assert str(e.value) == 'Value of file_value for MyCfg.a is invalid! Value: asdf'


def test_parse_flat_model():

    class MyCfg(ConfigModel):
        a: int = Field(7, file_value=10)
        b: str = 'asdf'

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(True)

    field_a = obj._easyconfig_get().model_values[0]
    assert field_a.name == 'a'
    assert field_a.path == ('a', )
    assert field_a.default_field == 7
    assert field_a.default_file == 10

    field_b = obj._easyconfig_get().model_values[1]
    assert field_b.name == 'b'
    assert field_b.path == ('b',)
    assert field_b.default_field == 'asdf'
    assert field_b.default_file == MISSING


def test_parse_sub_model():

    class SubCfg(ConfigModel):
        a: int = Field(7, file_value=10)

    class MyCfg(ConfigModel):
        a: SubCfg = SubCfg()
        b: str = 'asdf'

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(True)

    field_b = obj._easyconfig_get().model_values[0]
    assert field_b.name == 'b'
    assert field_b.path == ('b',)
    assert field_b.default_field == 'asdf'
    assert field_b.default_file == MISSING

    field_a = obj._easyconfig_get().model_models[0]
    assert field_a.name == 'a'
    assert field_a.path == ('a', )
    assert field_a.default_field == SubCfg(a=7)
    assert field_a.default_file == MISSING


@pytest.mark.parametrize('file_value', (MISSING, {'sub_a': 12}))
def test_parse_multiple_sub_models(file_value):

    class SubCfg(ConfigModel):
        sub_a: int = Field(7, file_value=10)

    class MyCfg(ConfigModel):
        a: SubCfg = Field(SubCfg(sub_a=8))
        b: SubCfg = Field(SubCfg(), file_value=MISSING if file_value is MISSING else SubCfg(**file_value))

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(True)

    field_a = obj._easyconfig_get().model_models[0]
    assert field_a.name == 'a'
    assert field_a.path == ('a',)
    assert field_a.default_field == SubCfg(sub_a=8)
    assert field_a.default_file is MISSING

    field_a_a = obj.a._easyconfig_get().model_values[0]
    assert field_a_a.name == 'sub_a'
    assert field_a_a.path == ('a', 'sub_a')
    assert field_a_a.default_field == 8
    assert field_a_a.default_file == 10

    field_b_a = obj.b._easyconfig_get().model_values[0]
    assert field_b_a.name == 'sub_a'
    assert field_b_a.path == ('b', 'sub_a')
    assert field_b_a.default_field == 7
    assert field_b_a.default_file == (10 if file_value is MISSING else file_value['sub_a'])


def test_parse_multiple_sub_sub_models():

    class SubSubCfg(ConfigModel):
        ssa: int = None
        ssb: int = Field(5, file_value=10)

    class SubCfg(ConfigModel):
        sa: SubSubCfg = Field(SubSubCfg(), file_value=SubSubCfg())
        sb: SubSubCfg = Field(SubSubCfg(), file_value=SubSubCfg(a=3))

    class MyCfg(ConfigModel):
        a: Optional[Dict[str, SubCfg]] = Field(None, file_value={'a': SubCfg(sa=SubSubCfg(ssa=8))})

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(True)

    field_a = obj._easyconfig_get().model_values[0]
    assert field_a.name == 'a'
    assert field_a.path == ('a',)
    assert field_a.default_field is None
    assert field_a.default_file == {
        'a': SubCfg(
            sa=SubSubCfg(ssa=8, ssb=5),
            sb=SubSubCfg(ssa=None, ssb=5))
    }
