from __future__ import annotations

import re
from pathlib import Path
from string import ascii_letters

from .location import ExpansionLocation, log

# https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
RE_WIN_PATH = re.compile(
    r'''
    (?:
        [a-zA-Z]:[/\\]   # Drive C:\path\file
    |
        (?:\\\\|//)      # UNC: \\server\share\path\file
    )
    [^''' + re.escape('<>:"|?*') + ']*',
    re.VERBOSE
)


def is_path(txt: str) -> bool:
    # absolute unix path
    if txt.startswith('/'):
        return True

    # absolute windows path
    if RE_WIN_PATH.match(txt):
        return True

    return False


def parse_path_key(txt: str) -> tuple[str, str | None]:
    parts = txt.split(':', 1)

    # we have no default
    if len(parts) == 1:
        return parts[0], None

    path, default = parts

    # check if the first entry is a windows path with a drive designator because
    # then we have to merge them back together
    if path not in ascii_letters:
        return path, default

    drive = path
    parts = default.split(':', 1)
    parts[0] = drive + ':' + parts[0]

    if len(parts) == 1:
        return parts[0], None

    path, default = parts
    return path, default


def read_file(name: str) -> str:
    # do it like this so we can patch the doc
    return Path(name).read_text().rstrip()


def read_file_contents(key: str, loc: ExpansionLocation) -> tuple[str, str | None]:
    name, default = parse_path_key(key)

    try:
        return name, read_file(name)
    except Exception as e:
        msg = f'Error while reading from file "{name:s}": ({e}) {loc.location_str()}'

        if default is not None:
            log.warning(msg)
            return name, default

        log.error(msg)
        return name, None
