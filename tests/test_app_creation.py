# ruff: noqa: RUF012

from enum import Enum

import pytest
from pydantic import BaseModel, Field, ValidationError

from easyconfig import create_app_config
from easyconfig.config_objs import AppConfig, ConfigObj
from easyconfig.errors import ExtraKwArgsNotAllowedError, FileDefaultsNotSetError
from easyconfig.models import AppBaseModel as EasyAppBaseModel
from easyconfig.models import BaseModel as EasyBaseModel


def test_simple() -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    create_app_config(SimpleModel(aaa=99))
    create_app_config(SimpleModel(), {'aaa': 999})

    with pytest.raises(ValidationError):
        create_app_config(SimpleModel(), {'aaa': 'asdf'})


def test_process() -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    msgs = []

    a = create_app_config(SimpleModel(aaa=99))
    a.load_preprocess.rename_entry(['zzz'], 'aaa').set_log_func(msgs.append)
    a.load_config_dict({'zzz': 999})

    assert a.a == 999
    assert msgs == ['Entry "zzz" renamed to "aaa"']


def test_default_yaml() -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    a = create_app_config(SimpleModel(aaa=99))
    assert a.generate_default_yaml() == 'aaa: 99\n'

    a = create_app_config(SimpleModel(), file_values=SimpleModel(aaa=12))
    assert a.generate_default_yaml() == 'aaa: 12\n'

    a = create_app_config(SimpleModel(), file_values=None)
    with pytest.raises(FileDefaultsNotSetError):
        a.generate_default_yaml()


def test_callback_for_default() -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    def get_default():
        return SimpleModel(aaa=999)

    a = create_app_config(SimpleModel(), get_default)
    assert a._file_defaults.a == 999

    a = create_app_config(SimpleModel(), lambda: {'aaa': 999})
    assert a._file_defaults.a == 999


def test_extra_kwargs() -> None:
    class SimpleModelOk(BaseModel):
        a: int = Field(5, alias='aaa', in_file=False)

    create_app_config(SimpleModelOk(aaa=99))

    class SimpleModelErr(BaseModel):
        a: int = Field(5, alias='aaa', in__file=False)

    with pytest.raises(ExtraKwArgsNotAllowedError) as e:
        create_app_config(SimpleModelErr(aaa=99))

    assert str(e.value) == 'Extra kwargs for field "a" of SimpleModelErr are not allowed: in__file'


def test_list_of_models() -> None:
    class MyEnum(str, Enum):
        A = 'aa'

    class SimpleModel(EasyBaseModel):
        a: int = Field(5, alias='aaa', in_file=False)
        b: int = Field(6)
        c: MyEnum = MyEnum.A

    class EncapModel(EasyBaseModel):
        c: list[SimpleModel] = []

    create_app_config(
        EncapModel(
            c=[
                SimpleModel(),
                SimpleModel(),
            ]
        )
    )


def test_path() -> None:
    class SimpleModel(EasyBaseModel):
        z: str = 'asdf'

    class ParentModel(EasyAppBaseModel):
        b: SimpleModel = SimpleModel()

    a = create_app_config(ParentModel())

    assert isinstance(a, AppConfig)
    assert isinstance(a.b, ConfigObj)

    a._file_path = o = object()

    assert a.loaded_file_path is o
    assert a.b.loaded_file_path is o
