from pydantic import BaseModel
from pydantic.fields import ModelField

from easyconfig.__const__ import MISSING
from easyconfig.yaml import CommentedMap


def cmap_from_model(model: BaseModel, skip_none=True) -> CommentedMap:
    cmap = CommentedMap()
    for obj_key, field in model.__fields__.items():  # type: str, ModelField
        value = getattr(model, obj_key, MISSING)
        if value is MISSING or (skip_none and value is None):
            continue

        yaml_key = field.alias
        description = field.field_info.description

        if isinstance(value, BaseModel):
            cmap[yaml_key] = cmap_from_model(value)
        else:
            # YAML can't serialize all data pydantic types natively, so we use the json serializer of the model
            # This works since a valid json is always a valid YAML. It's not nice but it's something!
            mode_cfg = model.__config__
            _json_value = mode_cfg.json_dumps(
                {'obj': value}, default=model.__json_encoder__)
            cmap[yaml_key] = mode_cfg.json_loads(_json_value)['obj']

        if not description:
            continue
        if yaml_key not in cmap.ca.items:
            cmap.yaml_add_eol_comment(description, yaml_key)

    return cmap
