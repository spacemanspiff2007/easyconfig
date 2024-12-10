from easyconfig.pre_process import RenameKeyPreProcess


def test_rename() -> None:
    f = RenameKeyPreProcess(('a', ), 'b')

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

    f = RenameKeyPreProcess(('a', 'd'), 'c')
    d = {'a': {'d': 1}}
    f.run(d)
    assert d == {'a': {'c': 1}}


def test_not_found() -> None:
    a = {}
    RenameKeyPreProcess(('a', ), 'b').run(a)
    assert a == {}


def test_no_overwrite() -> None:
    a = {'a': 1, 'b': 2}
    RenameKeyPreProcess(('a', ), 'b').run(a)
    assert a == {'a': 1, 'b': 2}
