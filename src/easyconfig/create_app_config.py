from collections.abc import Callable, Iterable
from inspect import isfunction
from typing import Any, TypeAlias, TypeVar

from pydantic import BaseModel

from easyconfig.__const__ import ARG_NAME_IN_FILE, MISSING, MISSING_TYPE
from easyconfig.config_objs.app_config import AppConfig, AsyncAppConfig, ConfigObj, yaml_rt
from easyconfig.errors import ExtraKwArgsNotAllowedError


TYPE_WRAPPED = TypeVar('TYPE_WRAPPED', bound=BaseModel)
TYPE_DEFAULTS: TypeAlias = BaseModel | dict[str, Any]


# noinspection PyProtectedMember
def check_field_args(model: ConfigObj, allowed: frozenset[str]) -> None:
    """Check extra args of pydantic fields"""

    # Model fields
    for name, field in model._obj_model_fields.items():
        if (extras := field.json_schema_extra) is None:
            continue
        if not set(extras).issubset(allowed):
            forbidden = sorted(set(extras) - allowed)
            msg = (
                f'Extra kwargs for field "{name}" of {model._obj_model_class.__name__} are not allowed: '
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
    model: BaseModel, file_values: MISSING_TYPE | None | TYPE_DEFAULTS | Callable[[], TYPE_DEFAULTS] = MISSING
) -> BaseModel | None:
    # Implicit default
    if file_values is MISSING:
        file_values = model

    # if it's a callback we get the values
    if isfunction(file_values):
        file_values = file_values()

    # dict -> build models
    if isinstance(file_values, dict):
        file_values = model.model_validate(file_values)

    if file_values is not None and not isinstance(file_values, BaseModel):
        msg = f'Default must be None or an instance of {BaseModel.__class__.__name__}! Got {type(file_values)}'
        raise ValueError(msg)

    return file_values


def _create_app_config(
    app_cls: type[AppConfig] | type[AsyncAppConfig],
    model: BaseModel,
    file_values: MISSING_TYPE | None | TYPE_DEFAULTS | Callable[[], TYPE_DEFAULTS] = MISSING, *,
    validate_file_values: bool = True,
    check_field_extra_args: Iterable[str] | None = (ARG_NAME_IN_FILE,),
) -> AppConfig | AsyncAppConfig:

    file_defaults = get_file_values(model, file_values)
    app_cfg = app_cls.from_model(model, file_defaults=file_defaults)

    # ensure that the extra args have no typos
    if check_field_extra_args is not None:
        check_field_args(app_cfg, frozenset(check_field_extra_args))

    # validate the default file
    if file_values is not None and validate_file_values:
        _yaml = app_cfg.generate_default_yaml()
        _dict = yaml_rt.load(_yaml)
        model.__class__.model_validate(_dict)

    return app_cfg


def create_app_config(
    model: TYPE_WRAPPED,
    file_values: MISSING_TYPE | None | TYPE_DEFAULTS | Callable[[], TYPE_DEFAULTS] = MISSING, *,
    validate_file_values: bool = True,
    check_field_extra_args: Iterable[str] | None = (ARG_NAME_IN_FILE,),
) -> TYPE_WRAPPED:

    return _create_app_config(
        AppConfig, model=model, file_values=file_values,
        validate_file_values=validate_file_values, check_field_extra_args=check_field_extra_args
    )


def create_async_app_config(
    model: TYPE_WRAPPED,
    file_values: MISSING_TYPE | None | TYPE_DEFAULTS | Callable[[], TYPE_DEFAULTS] = MISSING, *,
    validate_file_values: bool = True,
    check_field_extra_args: Iterable[str] | None = (ARG_NAME_IN_FILE,),
) -> TYPE_WRAPPED:

    return _create_app_config(
        AsyncAppConfig, model=model, file_values=file_values,
        validate_file_values=validate_file_values, check_field_extra_args=check_field_extra_args
    )

