# ruff: noqa: RUF012, INP001

from enum import Enum
from typing import List

import pytest
from pydantic import BaseModel, Field, ValidationError

from easyconfig import create_app_config
from easyconfig.errors import ExtraKwArgsNotAllowedError, FileDefaultsNotSetError
from easyconfig.models import BaseModel as EasyBaseModel


def test_simple():
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    create_app_config(SimpleModel(aaa=99))
    create_app_config(SimpleModel(), {'aaa': 999})

    with pytest.raises(ValidationError):
        create_app_config(SimpleModel(), {'aaa': 'asdf'})


def test_default_yaml():
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    a = create_app_config(SimpleModel(aaa=99))
    assert a.generate_default_yaml() == 'aaa: 99\n'

    a = create_app_config(SimpleModel(), file_values=SimpleModel(aaa=12))
    assert a.generate_default_yaml() == 'aaa: 12\n'

    a = create_app_config(SimpleModel(), file_values=None)
    with pytest.raises(FileDefaultsNotSetError):
        a.generate_default_yaml()


def test_callback_for_default():
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    def get_default():
        return SimpleModel(aaa=999)

    a = create_app_config(SimpleModel(), get_default)
    assert a._file_defaults.a == 999

    a = create_app_config(SimpleModel(), lambda: {'aaa': 999})
    assert a._file_defaults.a == 999


def test_extra_kwargs():
    class SimpleModelOk(BaseModel):
        a: int = Field(5, alias='aaa', in_file=False)

    create_app_config(SimpleModelOk(aaa=99))

    class SimpleModelErr(BaseModel):
        a: int = Field(5, alias='aaa', in__file=False)

    with pytest.raises(ExtraKwArgsNotAllowedError) as e:
        create_app_config(SimpleModelErr(aaa=99))

    assert str(e.value) == 'Extra kwargs for field "a" of SimpleModelErr are not allowed: in__file'


def test_list_of_models():
    class MyEnum(str, Enum):
        A = 'aa'

    class SimpleModel(EasyBaseModel):
        a: int = Field(5, alias='aaa', in_file=False)
        b: int = Field(6)
        c: MyEnum = MyEnum.A

    class EncapModel(EasyBaseModel):
        c: List[SimpleModel] = []

    create_app_config(
        EncapModel(
            c=[
                SimpleModel(),
                SimpleModel(),
            ]
        )
    )
