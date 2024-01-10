from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseModel, ByteSize, Field
from tests.helper import dump_yaml

from easyconfig.__const__ import ARG_NAME_IN_FILE
from easyconfig.yaml.from_model import cmap_from_model


def test_simple_model():
    class SimpleModel(BaseModel):
        a: int = 5
        b: int = 6

    assert dump_yaml(cmap_from_model(SimpleModel())) == 'a: 5\nb: 6\n'


def test_base_overrides():
    class SimpleModel(BaseModel):
        size: ByteSize
        url: AnyHttpUrl = 'http://test.de'

    assert dump_yaml(cmap_from_model(SimpleModel(size=ByteSize(1024)))) == 'size: 1024\nurl: http://test.de\n'


def test_simple_model_complex_types():
    class SimpleModel(BaseModel):
        a: datetime = datetime(2000, 1, 1)

    assert dump_yaml(cmap_from_model(SimpleModel())) == "a: '2000-01-01T00:00:00'\n"


def test_simple_model_skip_none():
    class SimpleModel(BaseModel):
        a: Optional[int] = 5
        b: int = 6

    assert dump_yaml(cmap_from_model(SimpleModel(a=None))) == 'b: 6\n'


def test_simple_model_alias():
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')
        b: int = 6

    assert dump_yaml(cmap_from_model(SimpleModel())) == 'aaa: 5\nb: 6\n'


def test_simple_model_description():
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa', description='Key A')
        b: int = Field(6, description='Key b')

    assert dump_yaml(cmap_from_model(SimpleModel())) == \
        'aaa: 5  # Key A\n' \
        'b: 6 # Key b\n'


def test_simple_model_skip_key():
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa', description='Key A')
        b: int = Field(6, description='Key b', **{ARG_NAME_IN_FILE: False})

    assert dump_yaml(cmap_from_model(SimpleModel())) == \
        'aaa: 5  # Key A\n'


def test_sub_model():
    class SubModel(BaseModel):
        aa: int = 5
        ab: int = 6

    class SimpleModel(BaseModel):
        a: SubModel = SubModel()
        b: int = 3

    assert dump_yaml(cmap_from_model(SimpleModel())) == '''a:
  aa: 5
  ab: 6
b: 3
'''


def test_skip_sub_model():
    class SubModel(BaseModel):
        aa: int = 5
        ab: int = 6

    class SimpleModel(BaseModel):
        a: SubModel = Field(SubModel(), **{ARG_NAME_IN_FILE: False})
        b: int = 3

    assert dump_yaml(cmap_from_model(SimpleModel())) == 'b: 3\n'


def test_sub_model_alias_description():
    class SubModel(BaseModel):
        aa: int = Field(5, alias='a', description='Key A')
        ab: int = 6

    class SimpleModel(BaseModel):
        a: SubModel = Field(SubModel(), description='Topmost Key A')
        b: int = 3

    assert dump_yaml(cmap_from_model(SimpleModel())) == '''a:  # Topmost Key A
  a: 5  # Key A
  ab: 6
b: 3
'''


def test_multiline_comment():
    class SimpleModel(BaseModel):
        a: str = Field('value a', description='This is\nthe topmost\nvalue of the model')
        b: int = Field(3, description='\nThis is\nvalue b')

    assert dump_yaml(cmap_from_model(SimpleModel())) == \
        'a: value a  # This is\n' \
        '# the topmost\n' \
        '# value of the model\n' \
        'b: 3 # \n' \
        '# This is\n' \
        '# value b\n'


def test_alias_not_in_file():
    class MyEnum(str, Enum):
        A = 'aa'

    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa', in_file=False)
        b: int = Field(6, description='Description value b')
        c: MyEnum = MyEnum.A

    class EncapModel(BaseModel):
        my_list: List[SimpleModel] = []

    assert dump_yaml(cmap_from_model(EncapModel(my_list=[SimpleModel(), SimpleModel(b=5), ]))) == \
        'my_list:\n' \
        '- b: 6  # Description value b\n' \
        '  c: aa\n' \
        '- b: 5  # Description value b\n' \
        '  c: aa\n'
