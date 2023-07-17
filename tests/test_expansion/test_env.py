import logging

from easyconfig.expansion.load_var import parse_env_key, read_env_var
from easyconfig.expansion.location import ExpansionLocation, log


def test_parse_env_key():
    assert parse_env_key('NAME') == ('NAME', None)
    assert parse_env_key('NAME:DEFAULT') == ('NAME', 'DEFAULT')
    assert parse_env_key('NAME:DEFAULT:MULTIPLE:COLON') == ('NAME', 'DEFAULT:MULTIPLE:COLON')

    assert parse_env_key('NAME:') == ('NAME', '')
    assert parse_env_key(':DEFAULT') == ('', 'DEFAULT')


def test_read_env_existing(envs: dict):
    envs.update({'NAME': 'asdf'})

    loc = ExpansionLocation(loc=(), stack=())
    assert read_env_var('NAME', loc=loc) == ('NAME', 'asdf')
    assert read_env_var('NAME:DEFAULT', loc=loc) == ('NAME', 'asdf')


def test_read_file_missing(caplog, envs):
    caplog.set_level(logging.DEBUG)
    loc = ExpansionLocation(loc=('key_1', ), stack=())

    assert read_env_var('DOES_NOT_EXIST', loc=loc) == ('DOES_NOT_EXIST', None)
    [[log_name, log_lvl, log_msg]] = caplog.record_tuples

    assert log_name == log.name
    assert log_lvl == logging.ERROR
    assert log_msg == 'Environment variable "DOES_NOT_EXIST" is not set or empty! (at __root__.key_1)'

    caplog.clear()

    assert read_env_var('DOES_NOT_EXIST:MY_DEFAULT', loc=loc) == ('DOES_NOT_EXIST', 'MY_DEFAULT')
    [[log_name, log_lvl, log_msg]] = caplog.record_tuples

    assert log_name == log.name
    assert log_lvl == logging.WARNING
    assert log_msg == 'Environment variable "DOES_NOT_EXIST" is not set or empty! (at __root__.key_1)'
