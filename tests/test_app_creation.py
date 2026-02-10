# ruff: noqa: RUF012
from collections.abc import Awaitable
from enum import Enum

import pytest
from pydantic import BaseModel, Field, ValidationError

from easyconfig import create_app_config, create_async_app_config
from easyconfig.config_objs import AppConfig, ConfigObj
from easyconfig.config_objs.app_config import AsyncAppConfig
from easyconfig.errors import ExtraKwArgsNotAllowedError, FileDefaultsNotSetError
from easyconfig.models import AppBaseModel as EasyAppBaseModel
from easyconfig.models import BaseModel as EasyBaseModel


@pytest.mark.parametrize('factory', (create_app_config, create_async_app_config))
def test_simple(factory) -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    factory(SimpleModel(aaa=99))
    factory(SimpleModel(), {'aaa': 999})

    with pytest.raises(ValidationError):
        create_app_config(SimpleModel(), {'aaa': 'asdf'})


@pytest.mark.parametrize('factory', (create_app_config, create_async_app_config))
async def test_process(factory) -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    msgs = []

    a = factory(SimpleModel(aaa=99))
    a.load_preprocess.rename_entry(['zzz'], 'aaa').set_log_func(msgs.append)

    obj = a.load_config_dict({'zzz': 999})
    if isinstance(obj, Awaitable):
        await obj

    assert a.a == 999
    assert msgs == ['Entry "zzz" renamed to "aaa"']


@pytest.mark.parametrize('factory', (create_app_config, create_async_app_config))
def test_default_yaml(factory) -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    a = factory(SimpleModel(aaa=99))
    assert a.generate_default_yaml() == 'aaa: 99\n'

    a = factory(SimpleModel(), file_values=SimpleModel(aaa=12))
    assert a.generate_default_yaml() == 'aaa: 12\n'

    a = factory(SimpleModel(), file_values=None)
    with pytest.raises(FileDefaultsNotSetError):
        a.generate_default_yaml()


@pytest.mark.parametrize('factory', (create_app_config, create_async_app_config))
def test_callback_for_default(factory) -> None:
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    def get_default():
        return SimpleModel(aaa=999)

    a = factory(SimpleModel(), get_default)
    assert a._file_defaults.a == 999

    a = factory(SimpleModel(), lambda: {'aaa': 999})
    assert a._file_defaults.a == 999


@pytest.mark.parametrize('factory', (create_app_config, create_async_app_config))
def test_extra_kwargs(factory) -> None:
    class SimpleModelOk(BaseModel):
        a: int = Field(5, alias='aaa', in_file=False)

    factory(SimpleModelOk(aaa=99))

    class SimpleModelErr(BaseModel):
        a: int = Field(5, alias='aaa', in__file=False)

    with pytest.raises(ExtraKwArgsNotAllowedError) as e:
        factory(SimpleModelErr(aaa=99))

    assert str(e.value) == 'Extra kwargs for field "a" of SimpleModelErr are not allowed: in__file'


@pytest.mark.parametrize('factory', (create_app_config, create_async_app_config))
def test_list_of_models(factory) -> None:
    class MyEnum(str, Enum):
        A = 'aa'

    class SimpleModel(EasyBaseModel):
        a: int = Field(5, alias='aaa', in_file=False)
        b: int = Field(6)
        c: MyEnum = MyEnum.A

    class EncapModel(EasyBaseModel):
        c: list[SimpleModel] = []

    factory(
        EncapModel(
            c=[
                SimpleModel(),
                SimpleModel(),
            ]
        )
    )


@pytest.mark.parametrize('factory', (create_app_config, create_async_app_config))
def test_path(factory) -> None:
    class SimpleModel(EasyBaseModel):
        z: str = 'asdf'

    class ParentModel(EasyAppBaseModel):
        b: SimpleModel = SimpleModel()

    a = factory(ParentModel())

    assert isinstance(a, AppConfig if factory is create_app_config else AsyncAppConfig)
    assert isinstance(a.b, ConfigObj)

    a._file_path = o = object()

    assert a.config_file_path is o
    assert a.b.config_file_path is o
