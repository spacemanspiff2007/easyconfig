import pytest

from easyconfig.pre_process.base import PathAccessor


def test_containing_obj() -> None:
    p = PathAccessor(('a', 'b'))
    assert p.get_containing_obj({}) is None

    d = {}
    assert p.get_containing_obj({'a': d}) is d

    p = PathAccessor(('a', 0, 'c', 'd'))
    assert p.get_containing_obj({'a': ({'c': d},)}) is d


def test_obj_exists() -> None:
    assert PathAccessor(('a', 'b')).obj_exists({}) is False
    assert PathAccessor(('a', )).obj_exists({'a': 1}) is True

    assert PathAccessor((1, )).obj_exists([1]) is False
    assert PathAccessor((0, )).obj_exists([1]) is True


def test_set_obj() -> None:
    assert PathAccessor(('a', 'b')).set_obj({}, 1) == {'b': 1}

    with pytest.raises(ValueError) as e:
        PathAccessor(('a', 'b')).set_obj({'b': 1}, 2)
    assert str(e.value) == 'Object a.b already exists'


def test_pop_obj() -> None:
    obj = {'b': 1}
    assert PathAccessor(('a', 'b')).pop_obj(obj) == 1
    assert obj == {}

    with pytest.raises(KeyError) as e:
        PathAccessor(('a', 'b')).pop_obj(obj) == 1
    assert str(e.value) == "'b'"

    obj = [0, 1, 2]
    assert PathAccessor((1, )).pop_obj(obj) == 1
    assert obj == [0, 2]
