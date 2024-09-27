import pytest

from easyconfig import BaseModel
from easyconfig.pre_process.move_keys import MoveKeyPreProcess


def test_containing_obj():
    f = MoveKeyPreProcess._get_containing_obj
    assert f({}, ('a', 'b')) is None

    d = {}
    assert f({'a': d}, ('a', 'b')) is d

    d = {}
    assert f({'a': ({'c': d},)}, ('a', 0, 'c', 'd')) is d


def test_obj_exists():
    f = MoveKeyPreProcess._obj_exists
    assert f({}, ('a', 'b')) is False
    assert f({}, ()) is False
    assert f({'a': 1}, ('a', )) is True

    assert f([1], (1, )) is False
    assert f([1], (0, )) is True


def test_move():
    f = MoveKeyPreProcess(('a', ), ('b', ))

    f.run({})

    d = {'b': 1}
    f.run(d)
    assert d == {'b': 1}

    d = {'a': 1}
    f.run(d)
    assert d == {'b': 1}

    d = {'a': {'c': 1}}
    f.run(d)
    assert d == {'b': {'c': 1}}

    f = MoveKeyPreProcess(('b', ), ('a', 'd'))
    d = {'a': {'c': 1}, 'b': 2}
    f.run(d)
    assert d == {'a': {'c': 1, 'd': 2}}


def test_move_dst_does_not_exist():
    class TestModelChildChild(BaseModel):
        db: int = 4

    class TestModelChild(BaseModel):
        b: int = 3
        c: TestModelChildChild = TestModelChildChild()

    class TestModel(BaseModel):
        a: TestModelChild = TestModelChild()

    f = MoveKeyPreProcess(('z', ), ('a', 'b'), defaults=TestModel())
    d = {'z': 2}
    f.run(d)
    assert d == {'a': {'b': 2}}

    with pytest.raises(ValueError) as e:
        MoveKeyPreProcess(('z', ), ('b', 'b', 'b'), defaults=TestModel())
    assert str(e.value) == 'Path "b.b" does not exist in default'

    with pytest.raises(ValueError) as e:
        MoveKeyPreProcess(('z', ), ('a', 'd', 'b'), defaults=TestModel())
    assert str(e.value) == 'Path "a.d" does not exist in default'
