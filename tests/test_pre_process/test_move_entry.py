import pytest

from easyconfig import BaseModel
from easyconfig.pre_process import MoveEntryPreProcess


def test_move() -> None:
    f = MoveEntryPreProcess(('a',), ('b',))

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

    msg = []
    f = MoveEntryPreProcess(('b',), ('a', 'd'))
    d = {'a': {'c': 1}, 'b': 2}
    f.run(d, msg.append)
    assert d == {'a': {'c': 1, 'd': 2}}
    assert msg == ['Entry "b" moved to "a.d"']


def test_move_tuple() -> None:
    class TestModelChildChild(BaseModel):
        i: int = 4

    class TestModelChild(BaseModel):
        c: tuple[TestModelChildChild, TestModelChildChild] = (TestModelChildChild(), TestModelChildChild())

    f = MoveEntryPreProcess(('z',), ('c', 1, 'i'), defaults=TestModelChild())
    d = {'z': 2}
    f.run(d)
    assert d == {'c': [{}, {'i': 2}, ]}


def test_move_dst_does_not_exist() -> None:
    class TestModelChildChild(BaseModel):
        db: int = 4

    class TestModelChild(BaseModel):
        b: int = 3
        c: TestModelChildChild = TestModelChildChild()

    class TestModel(BaseModel):
        a: TestModelChild = TestModelChild()

    f = MoveEntryPreProcess(('z',), ('a', 'b'), defaults=TestModel())
    d = {'z': 2}
    f.run(d)
    assert d == {'a': {'b': 2}}

    with pytest.raises(ValueError) as e:
        MoveEntryPreProcess(('z',), ('b', ), defaults=TestModel()).check(TestModel())
    assert str(e.value) == 'Path "b" does not exist in default'

    with pytest.raises(ValueError) as e:
        MoveEntryPreProcess(('z',), ('a', 'd'), defaults=TestModel()).check(TestModel())
    assert str(e.value) == 'Path "a.d" does not exist in default'

    with pytest.raises(ValueError) as e:
        MoveEntryPreProcess(('z',), ('a', 'c', 'd'), defaults=TestModel()).check(TestModel())
    assert str(e.value) == 'Path "a.c.d" does not exist in default'


def test_move_dst_does_not_exist_tuple() -> None:
    class TestModelChildChild(BaseModel):
        i: int = 4

    class TestModelChild(BaseModel):
        c: tuple[TestModelChildChild, TestModelChildChild] = (TestModelChildChild(), TestModelChildChild())

    with pytest.raises(ValueError) as e:
        MoveEntryPreProcess(('z',), ('c', 2, 'i'), defaults=TestModelChild()).check(TestModelChild())
    assert str(e.value) == 'Path "c.2" does not exist in default'

    with pytest.raises(ValueError) as e:
        MoveEntryPreProcess(('z',), ('c', 1, 'a'), defaults=TestModelChild()).check(TestModelChild())
    assert str(e.value) == 'Path "c.1.a" does not exist in default'
