from enum import Enum
from typing import Final, Literal


class _MissingType(Enum):
    MISSING_OBJ = object()

    def __str__(self):
        return '<Missing>'


MISSING: Final = _MissingType.MISSING_OBJ
MISSING_TYPE: Final = Literal[_MissingType.MISSING_OBJ]


ARG_NAME_IN_FILE: Final = 'in_file'
