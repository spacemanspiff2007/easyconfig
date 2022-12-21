from enum import Enum

from pydantic import BaseModel

from easyconfig.__const__ import ARG_NAME_IN_FILE, MISSING
from easyconfig.yaml import CommentedMap, CommentedSeq

NoneType = type(None)


def _get_yaml_value(obj, parent_model: BaseModel, skip_none=True):
    # Sometimes enum is used with int/str
    if isinstance(obj, Enum):
        return _get_yaml_value(obj.value, parent_model=parent_model, skip_none=skip_none)

    # yaml native datatypes
    if isinstance(obj, (int, float, str, bool, bytes, NoneType)):
        return obj

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

    # YAML can't serialize all data pydantic types natively, so we use the json serializer of the model
    # This works since a valid json is always a valid YAML. It's not nice but it's something!
    model_cfg = parent_model.__config__
    str_val = model_cfg.json_dumps(obj, default=parent_model.__json_encoder__)
    return model_cfg.json_loads(str_val)


def cmap_from_model(model: BaseModel, skip_none=True) -> CommentedMap:
    cmap = CommentedMap()
    for obj_key, field in model.__fields__.items():
        value = getattr(model, obj_key, MISSING)
        if value is MISSING or (skip_none and value is None):
            continue

        field_info = field.field_info

        yaml_key = field.alias
        description = field_info.description

        if not field_info.extra.get(ARG_NAME_IN_FILE, True):
            continue

        # get yaml representation
        cmap[yaml_key] = _get_yaml_value(value, parent_model=model)

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
