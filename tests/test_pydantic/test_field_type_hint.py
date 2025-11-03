import re
from pathlib import Path

import pydantic.fields
from pydantic.fields import FieldInfo

import easyconfig.models.field
from easyconfig.models import Field


def get_field_overloads(text: str, *, insert_in_file: bool = False) -> list[str]:
    without_comments = '\n'.join(line.split('#', 1)[0].rstrip() for line in text.splitlines())

    overloads = re.findall(r'@overload\ndef Field\([^)]+\) -> \w+: \.\.\.', without_comments)
    assert len(overloads) == 6

    if insert_in_file:
        for i, overload in enumerate(overloads):
            overloads[i] = overload.replace(
                '    **extra: Unpack[_EmptyKwargs],',
                '    in_file: bool = True,\n'
                '    **extra: Unpack[_EmptyKwargs],'
            )

    return overloads


def test_field_type_hint() -> None:

    target_overloads = get_field_overloads(Path(pydantic.fields.__file__).read_text(), insert_in_file=True)
    current_overloads = get_field_overloads(Path(easyconfig.models.field.__file__).read_text())

    for target, current in zip(target_overloads, current_overloads, strict=True):
        assert target == current, f'Field overload differs:\n{target}\n{current}'


def test_create_field() -> None:
    a = Field(alias='asdf')
    assert isinstance(a, FieldInfo)
