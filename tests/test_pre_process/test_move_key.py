import pytest

from easyconfig import BaseModel
from easyconfig.pre_process import MoveKeyPreProcess


def test_move() -> None:
    f = MoveKeyPreProcess(('a', ), ('b', ))

    d = {}
    f.run(d)
    assert d == {}

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


def test_move_dst_does_not_exist() -> None:
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
