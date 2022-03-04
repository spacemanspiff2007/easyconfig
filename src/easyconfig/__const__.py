from enum import Enum
from typing import Final, Literal


class _MissingType(Enum):
    MISSING = object()

    def __str__(self):
        return '<Missing>'


MISSING = _MissingType.MISSING
MISSING_TYPE = Literal[_MissingType.MISSING]


CREATION_DEFAULT_KEY: Final = 'file_value'
