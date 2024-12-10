from __future__ import annotations

from typing import TYPE_CHECKING, Any

from easyconfig.errors import FunctionCallNotAllowedError


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from easyconfig.config_objs import ConfigObjSubscription


class ConfigMixin:
    @property
    def loaded_file_path(self) -> Path:
        """Path to the loaded configuration file"""

    def subscribe_for_changes(self, func: Callable[[], Any], *,
                              propagate: bool = False, on_next_load: bool = True) -> ConfigObjSubscription:
        """When a value in this container changes the passed function will be called.

        :param func: function which will be called
        :param propagate: Propagate the change event to the parent object
        :param on_next_load: Call the function the next time when values get loaded even if there is no value change
        :return: object which can be used to cancel the subscription
        """

    # -----------------------------------------------------
    # pydantic 1
    @classmethod
    def parse_obj(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_raw(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_file(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def from_orm(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    # -----------------------------------------------------
    # pydantic 2
    @classmethod
    def model_validate_strings(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate_json(cls, *args: Any, **kwargs: Any):
        raise FunctionCallNotAllowedError()
