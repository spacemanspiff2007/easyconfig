from enum import Enum
from pathlib import Path

import pytest
from pydantic import Field, ValidationError

from easyconfig import ConfigModel


def test_default_validation():

    class A(ConfigModel):
        b: int = 'asdf'

        class Config:
            title = 'test'

    with pytest.raises(ValidationError) as f:
        A()
    assert str(f.value) == '1 validation error for A\nb\n  value is not a valid integer (type=type_error.integer)'

    class B(ConfigModel):
        b: int = Field(default_factory=lambda: Path('/folder'))

        class Config:
            title = 'test'

    with pytest.raises(ValidationError) as f:
        B()
    assert str(f.value) == '1 validation error for B\nb\n  value is not a valid integer (type=type_error.integer)'


def test_enum_values():
    """Test that the enum values get set instead of the enum object

    :return:
    """

    class MyStrEnum(str, Enum):
        T1 = 'TEXT1'
        T2 = 'TEXT2'

    class A(ConfigModel):
        b: MyStrEnum = MyStrEnum.T1

    assert A().b == 'TEXT1'
