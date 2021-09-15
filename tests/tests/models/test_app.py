from easyconfig import AppConfigModel, ConfigModel
from helper import Path


def test_load_flat():

    class MyCfg(AppConfigModel):
        a: int = 7
        b: str = 'asdf'

    o = MyCfg()
    p = Path('cfg.yml', initial_value="a: 8\nb: value")

    assert o.a == 7
    assert o.b == 'asdf'

    o.load_file(p)

    assert o.a == 8
    assert o.b == 'value'


def test_load_nested():

    class MyEntryA(ConfigModel):
        a1: int = 8
        a2: str = '1234'

    class MyEntryB(ConfigModel):
        b: float = 8.888

    class MyCfg(AppConfigModel):
        key_a: int = 7
        a: MyEntryA = MyEntryA()
        b: MyEntryB = MyEntryB()

    o = MyCfg()

    a = o.a
    b = o.b

    assert o.key_a == 7
    assert a.a1 == 8
    assert a.a2 == '1234'
    assert b.b == 8.888

    p = Path('cfg.yml', initial_value="a:\n  a1: 9\n  a2: '5768'")
    o.load_file(p)

    assert o.key_a == 7
    assert a.a1 == 9
    assert a.a2 == '5768'
    assert b.b == 8.888

    p = Path('cfg.yml', initial_value="b:\n  b: 5")
    o.load_file(p)

    assert o.key_a == 7
    assert a.a1 == 9    # <-- observe that the default values from before are not overwritten!
    assert a.a2 == '5768'
    assert b.b == 5.0


def test_create_flat():

    class MyCfg(AppConfigModel):
        a: int = 7
        b: str = 'asdf'

    o = MyCfg()
    p = Path('cfg.yml')

    assert o.a == 7
    assert o.b == 'asdf'

    o.load_file(p)

    assert o.a == 7
    assert o.b == 'asdf'

    assert p.get_value() == ''
