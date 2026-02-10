from __future__ import annotations

import logging
from dataclasses import dataclass

from typing_extensions import Self

from easyconfig.errors.errors import CyclicEnvironmentVariableReferenceError


log = logging.getLogger('easyconfig.expansion')


@dataclass(frozen=True)
class ExpansionLocation:
    loc: tuple[str, ...]        # location in the yaml
    stack: tuple[str, ...]      # stack for expansion of values

    def expand_value(self, name: str) -> Self:
        # value is valid
        new_stack = (*self.stack, name)
        if name in self.stack:
            msg = f'Cyclic environment variable reference: {" -> ".join(new_stack):s} {self.location_str()}'
            raise CyclicEnvironmentVariableReferenceError(msg)
        return self.__class__(loc=self.loc, stack=new_stack)

    def process_obj(self, name: str) -> Self:
        return self.__class__(
            loc=(
                *self.loc,
                name,
            ),
            stack=(),
        )

    def location_str(self) -> str:
        loc = ('__root__', *self.loc)
        return f'(at {".".join(loc)})'
