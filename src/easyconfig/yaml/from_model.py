from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from easyconfig.__const__ import ARG_NAME_IN_FILE, MISSING
from easyconfig.yaml import CommentedMap, CommentedSeq

NoneType = type(None)


def _get_yaml_value(obj, parent_model: BaseModel, *, skip_none=True, obj_name: str | None = None):
    if obj is None:
        return None

    # Sometimes enum is used with int/str
    if isinstance(obj, Enum):
        return _get_yaml_value(obj.value, parent_model=parent_model, skip_none=skip_none)

    # yaml native datatypes
    # Pydantic defines several validators that inherit from the python base type
    # Yaml can't represent those, so we cast them back to the native data type.
    for data_type in (bool, int, float, str, bytes):
        if isinstance(obj, data_type):
            return data_type(obj)

    if isinstance(obj, BaseModel):
        return cmap_from_model(obj, skip_none=skip_none)

    if isinstance(obj, (list, tuple, set, frozenset)):
        seq = CommentedSeq()
        for value in obj:
            seq.append(_get_yaml_value(value, parent_model=parent_model, skip_none=skip_none))
        return seq

    if isinstance(obj, dict):
        ret = CommentedMap()
        for key, value in obj.items():
            yaml_key = _get_yaml_value(key, parent_model=parent_model, skip_none=skip_none)
            ret[yaml_key] = _get_yaml_value(value, parent_model=parent_model, skip_none=skip_none)
        return ret

    # YAML can't serialize all data pydantic types natively, so we use the serializer of the model
    # This works since a valid json is always a valid YAML. It's not nice but it's something!
    dump = parent_model.model_dump(mode='json', include={obj_name})
    return dump[obj_name]


def cmap_from_model(model: BaseModel, skip_none=True) -> CommentedMap:
    cmap = CommentedMap()
    for obj_name, field in model.model_fields.items():
        value = getattr(model, obj_name, MISSING)
        if value is MISSING or (skip_none and value is None):
            continue

        yaml_key = field.alias
        if yaml_key is None:
            yaml_key = obj_name
        description = field.description

        if (extra_kwargs := field.json_schema_extra) is not None and not extra_kwargs.get(ARG_NAME_IN_FILE, True):
            continue

        # get yaml representation
        cmap[yaml_key] = _get_yaml_value(value, parent_model=model, obj_name=obj_name)

        if not description:
            continue

        # Don't overwrite comment
        if yaml_key not in cmap.ca.items:
            # Ensure that every line in the comment that has chars has a comment sign
            comment_lines = []
            for line in description.splitlines():
                _line = line.lstrip()
                comment_lines.append(('# ' + line) if _line and not _line.startswith('#') else line)

            cmap.yaml_add_eol_comment('\n'.join(comment_lines), yaml_key)

    return cmap
