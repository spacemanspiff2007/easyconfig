from typing import Tuple

from pydantic import Field

from easyconfig import AppConfigModel, ConfigModel
from easyconfig.yaml import CommentedMap
from helper import dump_yaml, Path


def test_value_no_comment():

    class MyCfg(ConfigModel):
        a: int = 7
        b: str = 'asdf'

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(set_default_value=True)

    map = CommentedMap()
    obj._easyconfig.update_map(map)
    assert dump_yaml(map) == 'a: 7\nb: asdf\n'


def test_value_with_comment():

    class MyCfg(ConfigModel):
        a: int = Field(7, description='this is an int')
        b: str = Field('asdf', description='this is a str')

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(set_default_value=True)

    map = CommentedMap()
    obj._easyconfig.update_map(map)
    assert dump_yaml(map) == 'a: 7  # this is an int\n' \
                             'b: asdf # this is a str\n'


def test_value_with_comment_alias():

    class MyCfg(AppConfigModel):
        a: int = Field(7, description='this is an int', alias='AA')
        b: str = Field('asdf', description='this is a str')

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(set_default_value=True)

    map = CommentedMap()
    obj._easyconfig.update_map(map)
    assert dump_yaml(map) == 'AA: 7  # this is an int\n' \
                             'b: asdf # this is a str\n'

    # check set by alias
    assert obj.a == 7
    p = Path('cfg.yml', initial_value="AA: 9")
    obj.load_file(p)
    assert obj.a == 9


def test_nested_value_with_default():

    class MyEntryC(ConfigModel):
        c: float = None
        d: str = 'is_c'

    class MyCfg(AppConfigModel):
        n: MyEntryC = MyEntryC(c=5.5)

    obj = MyCfg()

    map = CommentedMap()
    obj._easyconfig.update_map(map)

    assert dump_yaml(map) == 'n:\n' \
                             '  c: 5.5\n' \
                             '  d: is_c\n'


def test_nested_value_with_comment():

    class MyEntryC(ConfigModel):
        c: float = 8.888
        d: str = 'is_c'

    class MyCfg(ConfigModel):
        a: int = Field(7, description='this is an int')
        b: str = Field('asdf', description='this is a str')
        n: MyEntryC = Field(default_factory=MyEntryC, description='Model desc')

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(set_default_value=True)

    map = CommentedMap()
    obj._easyconfig.update_map(map)

    assert dump_yaml(map) == 'n:  # Model desc\n' \
                             '  c: 8.888\n' \
                             '  d: is_c\n' \
                             'a: 7 # this is an int\n' \
                             'b: asdf # this is a str\n'


def test_nested_tuple_value_with_comment():

    class MyEntryC(ConfigModel):
        c: float = 8.888
        d: str = 'is_c'

    class MyCfg(ConfigModel):
        a: int = Field(7, description='this is an int')
        b: str = Field('asdf', description='this is a str')
        n: Tuple[MyEntryC, MyEntryC, MyEntryC] = Field(
            default_factory=lambda: (MyEntryC(), MyEntryC(), MyEntryC()), description='Model desc')

    obj = MyCfg()
    obj._easyconfig_initialize().parse_model(set_default_value=True)

    map = CommentedMap()
    obj._easyconfig.update_map(map)

    assert dump_yaml(map) == 'n:  # Model desc\n' \
                             '- c: 8.888\n' \
                             '  d: is_c\n' \
                             '- c: 8.888\n' \
                             '  d: is_c\n' \
                             '- c: 8.888\n' \
                             '  d: is_c\n' \
                             'a: 7 # this is an int\n' \
                             'b: asdf # this is a str\n'
