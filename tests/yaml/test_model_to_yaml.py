from datetime import datetime
from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, ByteSize
from pydantic import Field as PydanticField
from tests.helper import dump_yaml

from easyconfig import Field
from easyconfig.__const__ import ARG_NAME_IN_FILE
from easyconfig.yaml.from_model import cmap_from_model


def test_simple_model() -> None:
    class SimpleModel(BaseModel):
        a: int = 5
        b: int = 6

    assert dump_yaml(cmap_from_model(SimpleModel())) == 'a: 5\nb: 6\n'


def test_base_overrides() -> None:
    class SimpleModel(BaseModel):
        size: ByteSize
        url: AnyHttpUrl = 'http://test.de'

    assert dump_yaml(cmap_from_model(SimpleModel(size=ByteSize(1024)))) == 'size: 1024\nurl: http://test.de\n'


def test_simple_model_complex_types() -> None:
    class SimpleModel(BaseModel):
        a: datetime = datetime(2000, 1, 1)

    assert dump_yaml(cmap_from_model(SimpleModel())) == "a: '2000-01-01T00:00:00'\n"


def test_simple_model_skip_none() -> None:
    class SimpleModel(BaseModel):
        a: int | None = 5
        b: int = 6

    assert dump_yaml(cmap_from_model(SimpleModel(a=None))) == 'b: 6\n'


def test_simple_model_alias() -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')
        b: int = 6

    assert dump_yaml(cmap_from_model(SimpleModel())) == 'aaa: 5\nb: 6\n'


def test_simple_model_description() -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa', description='Key A')
        b: int = Field(6, description='Key b')

    assert dump_yaml(cmap_from_model(SimpleModel())) == (
        'aaa: 5  # Key A\n'
        'b: 6 # Key b\n'
    )


def test_simple_model_skip_key() -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa', description='Key A')
        b: int = Field(6, description='Key b', **{ARG_NAME_IN_FILE: False})

    assert dump_yaml(cmap_from_model(SimpleModel())) == \
        'aaa: 5  # Key A\n'


def test_sub_model() -> None:
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


def test_skip_sub_model() -> None:
    target = 'b: 3\n'

    class SubModel(BaseModel):
        aa: int = 5
        ab: int = 6

    class SimpleModel(BaseModel):
        a: SubModel = Field(SubModel(), **{ARG_NAME_IN_FILE: False})
        b: int = 3

    assert dump_yaml(cmap_from_model(SimpleModel())) == target

    class SimpleModel(BaseModel):
        a: SubModel = PydanticField(SubModel(), **{ARG_NAME_IN_FILE: False})
        b: int = 3

    assert dump_yaml(cmap_from_model(SimpleModel())) == target


def test_sub_model_alias_description() -> None:
    class SubModel(BaseModel):
        aa: int = Field(5, alias='a', description='Key A')
        ab: int = 6

    class SimpleModel(BaseModel):
        a: SubModel = Field(SubModel(), description='Topmost Key A')
        b: int = 3

    assert dump_yaml(cmap_from_model(SimpleModel())) == (
        'a:  # Topmost Key A\n'
        '  a: 5  # Key A\n'
        '  ab: 6\n'
        'b: 3\n'
    )


def test_multiline_comment() -> None:
    class SimpleModel(BaseModel):
        a: str = Field('value a', description='This is\nthe topmost\nvalue of the model')
        b: int = Field(3, description='\nThis is\nvalue b')

    assert dump_yaml(cmap_from_model(SimpleModel())) == (
        'a: value a  # This is\n'
        '# the topmost\n'
        '# value of the model\n'
        'b: 3 # \n'
        '# This is\n'
        '# value b\n'
    )


def test_alias_not_in_file() -> None:
    class MyEnum(str, Enum):
        A = 'aa'

    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa', in_file=False)
        b: int = Field(6, description='Description value b')
        c: MyEnum = MyEnum.A

    class EncapModel(BaseModel):
        my_list: list[SimpleModel] = []

    assert dump_yaml(cmap_from_model(EncapModel(my_list=[SimpleModel(), SimpleModel(b=5), ]))) == (
        'my_list:\n'
        '- b: 6  # Description value b\n'
        '  c: aa\n'
        '- b: 5  # Description value b\n'
        '  c: aa\n'
    )
