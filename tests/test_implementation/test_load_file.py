from pydantic import BaseModel

from easyconfig.config_objs import AppConfig
from helper import Path


def test_mutate_simple():
    class SimpleModel(BaseModel):
        a: int = 5
        b: int = 6

    cfg = AppConfig.from_model(SimpleModel())

    assert cfg.a == 5
    assert cfg.b == 6

    file = Path('test_file.yml', initial_value='a: 7\nb: 9')
    cfg.load_config_file(file)

    assert cfg.a == 7
    assert cfg.b == 9


def test_mutate_nested():
    class SubModel(BaseModel):
        aa: int = 5

    class SimpleModel(BaseModel):
        a: SubModel = SubModel()
        b: SubModel = SubModel(aa=7)
        c: int = 3

    cfg = AppConfig.from_model(SimpleModel())

    a = cfg.a
    b = cfg.b

    assert cfg.c == 3
    assert cfg.a is a and a.aa == 5
    assert cfg.b is b and b.aa == 7

    file = Path('test_file.yml', initial_value='a:\n  aa: 7\nb:\n  aa: 9\nc: 5')
    cfg.load_config_file(file)

    assert cfg.c == 5
    assert cfg.a is a and a.aa == 7
    assert cfg.b is b and b.aa == 9
