# ruff: noqa: RUF012

import datetime
from typing import Dict, Set

from pydantic import (
    AnyHttpUrl,
    ByteSize,
    ConfigDict,
    NegativeFloat,
    StrictBool,
    StrictBytes,
    StrictInt,
    condate,
    confloat,
    conint,
    conlist,
    conset,
    constr,
)
from pydantic import BaseModel as _BaseModel

from easyconfig.yaml import CommentedMap, CommentedSeq
from easyconfig.yaml.from_model import _get_yaml_value


class BaseModel(_BaseModel):
    model_config = ConfigDict(validate_assignment=True, validate_default=True, extra='forbid')


def cmp_value(obj, target) -> None:
    assert obj == target
    assert type(obj) is type(target)


def test_built_in_types() -> None:
    class ConstrainedModel(BaseModel):
        is_bool: bool = True
        is_int: int = 10
        is_str: str = 'asdf1!'

        is_dict: Dict[str, int] = {'asdf': '10'}
        is_set: Set[int] = {'10'}

    m = ConstrainedModel()

    assert _get_yaml_value(m.is_bool, m) is True
    cmp_value(_get_yaml_value(m.is_int, m), 10)
    cmp_value(_get_yaml_value(m.is_str, m), 'asdf1!')

    cmp_value(_get_yaml_value(m.is_dict, m), CommentedMap({'asdf': 10}))
    cmp_value(_get_yaml_value(m.is_set, m), CommentedSeq([10]))


def test_constrained_types() -> None:
    class ConstrainedModel(BaseModel):
        negative_float: NegativeFloat = -5
        negative_int: NegativeFloat = -3

        con_float: confloat(ge=10) = 11
        con_int: conint(ge=10) = 11
        con_str: constr(strip_whitespace=True) = '  asdf  '

        con_list: conlist(str) = ['1']
        con_set: conset(bool) = {1}

        con_date: condate(ge=datetime.date(2023, 1, 1)) = datetime.date(2023, 1, 2)

    m = ConstrainedModel()

    cmp_value(_get_yaml_value(m.negative_float, m), -5.0)
    cmp_value(_get_yaml_value(m.negative_int, m), -3.0)

    cmp_value(_get_yaml_value(m.con_float, m), 11.0)
    cmp_value(_get_yaml_value(m.con_int, m), 11)
    cmp_value(_get_yaml_value(m.con_str, m), 'asdf')

    cmp_value(_get_yaml_value(m.con_list, m, obj_name='con_list'), CommentedSeq(['1']))
    cmp_value(_get_yaml_value(m.con_set, m, obj_name='con_list'), CommentedSeq([True]))

    cmp_value(_get_yaml_value(m.con_date, m, obj_name='con_date'), '2023-01-02')  # yaml can't natively serialize dates


def test_strict_types() -> None:
    class StrictModel(BaseModel):
        strict_bool_true: StrictBool = True
        strict_bool_false: StrictBool = False

        strict_int_0: StrictInt = 0
        strict_int_100: StrictInt = StrictInt(100)

        strict_bytes: StrictBytes = b'asdf'
        strict_bytes_empty: StrictBytes = StrictBytes(b'')

    m = StrictModel()

    assert _get_yaml_value(m.strict_bool_true, m) is True
    assert _get_yaml_value(m.strict_bool_false, m) is False

    cmp_value(_get_yaml_value(m.strict_int_0, m), 0)
    cmp_value(_get_yaml_value(m.strict_int_100, m), 100)

    cmp_value(_get_yaml_value(m.strict_bytes, m), b'asdf')
    cmp_value(_get_yaml_value(m.strict_bytes_empty, m), b'')


def test_more_types() -> None:
    class SimpleModel(BaseModel):
        size_raw: ByteSize = 100
        size_str: ByteSize = '10kb'
        size_obj: ByteSize = ByteSize(50)
        url: AnyHttpUrl = 'http://test.de/asdf'

    m = SimpleModel()

    assert _get_yaml_value(m.size_raw, m) == 100
    assert _get_yaml_value(m.size_str, m) == 10_000
    assert _get_yaml_value(m.size_obj, m) == 50
    assert _get_yaml_value(m.url, m, obj_name='url') == 'http://test.de/asdf'
