import pytest
from pydantic import BaseModel as PydanticBaseModel

from helper import Path

from easyconfig import AppBaseModel, BaseModel
from easyconfig.config_objs import AppConfig


@pytest.mark.parametrize('base_cls', [PydanticBaseModel, BaseModel, AppBaseModel])
def test_mutate_simple(base_cls):
    class SimpleModel(base_cls):
        a: int = 5
        b: int = 6

    cfg = AppConfig.from_model(SimpleModel())

    assert cfg.a == 5
    assert cfg.b == 6

    file = Path('test_file.yml', initial_value='a: 7\nb: 9')
    cfg.load_config_file(file)

    assert cfg.a == 7
    assert cfg.b == 9


@pytest.mark.parametrize('base_cls', [PydanticBaseModel, BaseModel, AppBaseModel])
def test_mutate_nested(base_cls):
    class SubModel(base_cls):
        aa: int = 5

    class SimpleModel(PydanticBaseModel):
        a: SubModel = SubModel()
        b: SubModel = SubModel(aa=7)
        c: int = 3

    cfg = AppConfig.from_model(SimpleModel())

    a = cfg.a
    b = cfg.b

    assert cfg.c == 3
    assert cfg.a is a and a.aa == 5  # noqa: PT018
    assert cfg.b is b and b.aa == 7  # noqa: PT018

    file = Path('test_file.yml', initial_value='a:\n  aa: 7\nb:\n  aa: 9\nc: 5')
    cfg.load_config_file(file)

    assert cfg.c == 5
    assert cfg.a is a and a.aa == 7  # noqa: PT018
    assert cfg.b is b and b.aa == 9  # noqa: PT018

    file = Path('test_file.yml', initial_value='a:\n  aa: 77\nb:\n  aa: 99\nc: 9')
    cfg.load_config_file(file)

    assert cfg.c == 9
    assert cfg.a is a and a.aa == 77  # noqa: PT018
    assert cfg.b is b and b.aa == 99  # noqa: PT018
