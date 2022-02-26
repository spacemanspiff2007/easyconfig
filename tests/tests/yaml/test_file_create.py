from pydantic import Field

from easyconfig import AppConfigModel, ConfigModel
from helper import Path


class SubModel(ConfigModel):
    a: str = None


class MyTestModel(ConfigModel):
    sub: SubModel = Field(default_factory=lambda: SubModel(a='test'), alias='b')


class MyCfg(AppConfigModel):
    name: MyTestModel = MyTestModel()


def test_load():
    p = Path('testfile.yml', does_exist=False)

    config = MyCfg()
    assert config.name.sub.a == 'test'

    config.load_file(p)

    file = p.contents.getvalue()
    assert file == 'name:\n  b:\n    a: test\n'
