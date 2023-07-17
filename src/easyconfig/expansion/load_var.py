from __future__ import annotations

from os import environ

from .location import ExpansionLocation, log


def parse_env_key(key: str) -> tuple[str, str | None]:
    parts = key.split(':', 1)
    if len(parts) == 1:
        return parts[0], None

    key, default = parts
    return key, default


def read_env_var(key: str, loc: ExpansionLocation) -> tuple[str, str | None]:
    name, default = parse_env_key(key)

    if (value := environ.get(name)) is not None:
        return name, value

    msg = f'Environment variable "{name:s}" is not set or empty! {loc.location_str()}'

    if default is not None:
        log.warning(msg)
        return name, default

    log.error(msg)
    return name, None
