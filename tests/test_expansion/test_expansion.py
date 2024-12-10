import pytest

from easyconfig.errors.errors import CyclicEnvironmentVariableReferenceError
from easyconfig.expansion.expand import RE_REPLACE, expand_obj, expand_text
from easyconfig.expansion.location import ExpansionLocation


def test_regex() -> None:
    assert RE_REPLACE.fullmatch('${}')
    assert RE_REPLACE.fullmatch('${asdf}')

    assert not RE_REPLACE.search('$${}')
    assert not RE_REPLACE.search('$${asdf}')

    assert RE_REPLACE.search('${asdf${asdf}').group(1) == 'asdf${asdf'
    assert RE_REPLACE.search('${${}').group(1) == '${'


def test_load_env(envs: dict) -> None:
    envs.update(
        {'NAME': 'asdf', 'RECURSE': 'Name: ${NAME}', 'TEST_$_DOLLAR': 'DOLLAR_WORKS', 'TEST_}_CURLY': 'CURLY_WORKS'}
    )

    loc = ExpansionLocation((), ())

    assert expand_text('${NAME}', loc) == 'asdf'
    assert expand_text('${NOT_EXIST}', loc) == ''
    assert expand_text('${NOT_EXIST:DEFAULT}', loc) == 'DEFAULT'

    assert expand_text('Test ${RECURSE}', loc) == 'Test Name: asdf'

    assert expand_text('Test ${RECURSE}', loc) == 'Test Name: asdf'

    assert expand_text('${TEST_$_DOLLAR}', loc) == 'DOLLAR_WORKS'

    # escape expansion
    assert expand_text('$${}', loc) == '${}'
    assert expand_text('$${NAME}', loc) == '${NAME}'
    assert expand_text('$${:ASDF}', loc) == '${:ASDF}'
    assert expand_text('$${NAME:DEFAULT}', loc) == '${NAME:DEFAULT}'

    # escape closing bracket
    assert expand_text('${MISSING:DEFAULT$}_}', loc) == 'DEFAULT}_'
    assert expand_text('${TEST_$}_CURLY}', loc) == 'CURLY_WORKS'


def test_env_cyclic_reference(envs: dict) -> None:
    envs.update({'NAME': '${SELF}', 'SELF': 'Name: ${SELF}'})

    with pytest.raises(CyclicEnvironmentVariableReferenceError) as e:
        assert expand_text('Test self: ${NAME}', loc=ExpansionLocation(loc=('a',), stack=())) == 'asdf'

    assert str(e.value) == 'Cyclic environment variable reference: NAME -> SELF -> SELF (at __root__.a)'


def test_expansion(envs: dict) -> None:
    envs.update({'NAME': 'ASDF'})

    obj = {'a': {'b': ['${NAME}']}, 'b': '${MISSING:DEFAULT}'}

    expand_obj(obj)

    assert obj == {'a': {'b': ['ASDF']}, 'b': 'DEFAULT'}
