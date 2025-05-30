from __future__ import annotations

import re
from typing import Any

from .load_file import is_path, read_file_contents
from .load_var import read_env_var
from .location import ExpansionLocation


RE_REPLACE = re.compile(r'''
    (?<!\$)\$\{
        (?P<value>.*?[^$])?
    (?!\$)}
''', re.VERBOSE)


RE_ESCAPED = re.compile(RE_REPLACE.pattern.replace(r'(?<!\$)', r'\$'), re.VERBOSE)


def read_value(key: str, /, loc: ExpansionLocation) -> tuple[str, str]:
    if is_path(key):
        name, value = read_file_contents(key, loc)
    else:
        name, value = read_env_var(key, loc)

    if value is None:
        value = ''
    return name, value


def expand_text(text: str, /, loc: ExpansionLocation):
    if not isinstance(text, str):
        return text

    if '$' not in text:
        return text

    pos_start = 0

    while m := RE_REPLACE.search(text, pos_start):
        m_start = m.start()
        m_end = m.end()

        raw_value = m.group('value')
        raw_value = raw_value.replace('$}', '}')

        name, value = read_value(raw_value, loc=loc)

        # value is valid
        value = expand_text(value, loc=loc.expand_value(name))
        text = text[:m_start] + value + text[m_end:]

    # escaped expansion
    if '$$' in text:
        text = RE_ESCAPED.sub(r'${\g<value>}', text)
    return text


def expand_obj(obj: Any, loc: ExpansionLocation | None = None):
    if loc is None:
        loc = ExpansionLocation((), ())

    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = expand_obj(value, loc.process_obj(str(key)))
        return obj

    if isinstance(obj, list):
        for i, value in enumerate(obj):
            obj[i] = expand_obj(value, loc.process_obj(f'[{i:d}]'))
        return obj

    return expand_text(obj, loc)
