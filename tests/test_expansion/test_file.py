import logging

import pytest

from easyconfig.expansion.load_file import is_path, parse_path_key, read_file_contents
from easyconfig.expansion.location import ExpansionLocation, log


@pytest.mark.parametrize(
    'txt', [pytest.param('c:/path/file', id='p1'), pytest.param('//server/share/path/file', id='p2')]
)
def test_is_path_win(txt: str) -> None:
    assert is_path(txt)
    assert is_path(txt.upper())

    txt = txt.replace('/', '\\')
    assert is_path(txt)
    assert is_path(txt.upper())


def test_is_path() -> None:
    # unix path
    assert is_path('/asdf')
    assert is_path('/asdf.txt')

    # we require absolute paths
    assert not is_path('asdf.txt')


def test_parse_path() -> None:
    assert parse_path_key('c:/path/file') == ('c:/path/file', None)
    assert parse_path_key('//server/share/path/file') == ('//server/share/path/file', None)
    assert parse_path_key('/asdf') == ('/asdf', None)

    assert parse_path_key('c:/path/file:MY_DEFAULT') == ('c:/path/file', 'MY_DEFAULT')
    assert parse_path_key('//server/share/path/file:MY_DEFAULT') == ('//server/share/path/file', 'MY_DEFAULT')
    assert parse_path_key('/asdf:MY_DEFAULT') == ('/asdf', 'MY_DEFAULT')

    assert parse_path_key('c:/path/file:MY_DEFAULT:WITH:MORE') == ('c:/path/file', 'MY_DEFAULT:WITH:MORE')
    assert parse_path_key('//server/share/path/file:MY_DEFAULT:WITH:MORE') == (
        '//server/share/path/file',
        'MY_DEFAULT:WITH:MORE',
    )
    assert parse_path_key('/asdf:MY_DEFAULT:WITH:MORE') == ('/asdf', 'MY_DEFAULT:WITH:MORE')


def test_read_file_existing(caplog, tmp_path) -> None:
    caplog.set_level(logging.DEBUG)
    loc = ExpansionLocation(loc=(), stack=())

    file = tmp_path / 'tmp.txt'
    file.write_text('asdf asdf\n\n')

    name, value = read_file_contents(str(file), loc=loc)
    assert name == str(file)
    assert value == 'asdf asdf'

    name, value = read_file_contents(f'{file.as_posix()}:DEFAULT', loc=loc)
    assert name == file.as_posix()
    assert value == 'asdf asdf'


def test_read_file_missing(caplog) -> None:
    caplog.set_level(logging.DEBUG)
    loc = ExpansionLocation(loc=('key_1',), stack=())

    assert read_file_contents('/does/not/exist', loc=loc) == ('/does/not/exist', None)
    [[log_name, log_lvl, log_msg]] = caplog.record_tuples

    assert log_name == log.name
    assert log_lvl == logging.ERROR
    assert log_msg.startswith('Error while reading from file "/does/not/exist": ')
    assert log_msg.endswith(' (at __root__.key_1)')

    caplog.clear()

    assert read_file_contents('/does/not/exist:MY_DEFAULT', loc=loc) == ('/does/not/exist', 'MY_DEFAULT')
    [[log_name, log_lvl, log_msg]] = caplog.record_tuples

    assert log_name == log.name
    assert log_lvl == logging.WARNING
    assert log_msg.startswith('Error while reading from file "/does/not/exist": ')
    assert log_msg.endswith(' (at __root__.key_1)')
