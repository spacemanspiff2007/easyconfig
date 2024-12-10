import pytest

from easyconfig import BaseModel
from easyconfig.pre_process import DeleteEntryPreProcess


def test_delete_root() -> None:
    f = DeleteEntryPreProcess(('a',))

    d = {}
    f.run(d)
    assert d == {}

    d = {'b': 1}
    f.run(d)
    assert d == {'b': 1}

    d = {'a': 1}
    f.run(d)
    assert d == {}

    d = {'a': {'c': 1}}
    f.run(d)
    assert d == {}

    d = {'b': {'c': 1}}
    f.run(d)
    assert d == {'b': {'c': 1}}


def test_delete_nested() -> None:
    f = DeleteEntryPreProcess(('a', 'b'))

    d = {}
    f.run(d)
    assert d == {}

    d = {'b': 1}
    f.run(d)
    assert d == {'b': 1}

    d = {'a': 1}
    f.run(d)
    assert d == {'a': 1}

    msg = []
    d = {'a': {'b': 1}}
    f.run(d, msg.append)
    assert d == {'a': {}}
    assert msg == ['Entry "a.b" was deleted']

    d = {'a': {'c': 1}}
    f.run(d)
    assert d == {'a': {'c': 1}}

