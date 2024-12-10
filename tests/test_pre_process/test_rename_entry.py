from easyconfig.pre_process import RenameEntryPreProcess


def test_rename() -> None:
    f = RenameEntryPreProcess(('a',), 'b')
    f.run({})

    d = {'b': 1}
    f.run(d)
    assert d == {'b': 1}

    msg = []
    d = {'a': 1}
    f.run(d, log_func=msg.append)
    assert d == {'b': 1}
    assert msg == ['Entry "a" renamed to "b"']

    d = {'a': {'c': 1}}
    f.run(d)
    assert d == {'b': {'c': 1}}

    msg = []
    f = RenameEntryPreProcess(('a', 'd'), 'c')
    d = {'a': {'d': 1}}
    f.run(d, msg.append)
    assert d == {'a': {'c': 1}}
    assert msg == ['Entry "d" renamed to "c" in "a"']


def test_not_found() -> None:
    a = {}
    RenameEntryPreProcess(('a',), 'b').run(a)
    assert a == {}


def test_no_overwrite() -> None:
    a = {'a': 1, 'b': 2}
    RenameEntryPreProcess(('a',), 'b').run(a)
    assert a == {'a': 1, 'b': 2}
