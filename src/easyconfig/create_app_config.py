from inspect import isfunction
from typing import Any, Callable, Dict, FrozenSet, Iterable, Optional, TypeVar, Union

from pydantic import BaseModel

from easyconfig.__const__ import ARG_NAME_IN_FILE, MISSING, MISSING_TYPE
from easyconfig.config_objs.app_config import AppConfig, yaml_rt
from easyconfig.errors import ExtraKwArgsNotAllowedError

TYPE_WRAPPED = TypeVar('TYPE_WRAPPED', bound=BaseModel)
TYPE_DEFAULTS = Union[BaseModel, Dict[str, Any]]


# noinspection PyProtectedMember
def check_field_args(model: AppConfig, allowed: FrozenSet[str]):
    """Check extra args of pydantic fields"""

    # Model fields
    for name, field in model._obj_model_fields.items():
        if (extras := field.json_schema_extra) is None:
            continue
        if not set(extras).issubset(allowed):
            forbidden = sorted(set(extras) - allowed)
            msg = (
                f'Extra kwargs for field "{name}" of {model._last_model.__class__.__name__} are not allowed: '
                f'{", ".join(forbidden)}'
            )
            raise ExtraKwArgsNotAllowedError(msg)

    # Submodels
    for sub_model in model._obj_children.values():
        if isinstance(sub_model, tuple):
            for _sub_model in sub_model:
                check_field_args(model, allowed)
        else:
            check_field_args(sub_model, allowed)


def get_file_values(
    model: TYPE_WRAPPED, file_values: Union[MISSING_TYPE, None, TYPE_DEFAULTS, Callable[[], TYPE_DEFAULTS]] = MISSING
) -> Optional[BaseModel]:
    # Implicit default
    if file_values is MISSING:
        file_values = model

    # if it's a callback we get the values
    if isfunction(file_values):
        file_values = file_values()

    # dict -> build models
    if isinstance(file_values, dict):
        file_values = model.__class__.parse_obj(file_values)

    if file_values is not None and not isinstance(file_values, BaseModel):
        msg = f'Default must be None or an instance of {BaseModel.__class__.__name__}! Got {type(file_values)}'
        raise ValueError(msg)

    return file_values


def create_app_config(
    model: TYPE_WRAPPED,
    file_values: Union[MISSING_TYPE, None, TYPE_DEFAULTS, Callable[[], TYPE_DEFAULTS]] = MISSING,
    validate_file_values=True,
    check_field_extra_args: Optional[Iterable[str]] = (ARG_NAME_IN_FILE,),
) -> TYPE_WRAPPED:
    app_cfg = AppConfig.from_model(model)
    app_cfg._file_defaults = get_file_values(model, file_values)

    # ensure that the extra args have no typos
    if check_field_extra_args is not None:
        check_field_args(app_cfg, frozenset(check_field_extra_args))

    # validate the default file
    if file_values is not None and validate_file_values:
        _yaml = app_cfg.generate_default_yaml()
        _dict = yaml_rt.load(_yaml)
        model.__class__.model_validate(_dict)

    return app_cfg
