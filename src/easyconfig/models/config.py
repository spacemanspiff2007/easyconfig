from __future__ import annotations

from typing import TYPE_CHECKING, Any, NoReturn

from typing_extensions import Self

from easyconfig.errors import FunctionCallNotAllowedError


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from easyconfig.config_objs import ConfigObjSubscription


class ConfigMixin:
    @property
    def config_file_path(self) -> Path:
        """Path to the loaded configuration file"""

    def subscribe_set_options(self, *, propagate: bool | None = None, on_next_value: bool | None = None) -> Self:
        """Set options for the subscription of this object.

        :param propagate: Propagate the change event to the parent object
        :param on_next_value: Call the function the next time when values get loaded even if there is no value change
        """

    def subscribe_for_changes(self, func: Callable[[], Any]) -> ConfigObjSubscription:
        """When a value in this container changes the passed function will be called.

        :param func: function which will be called
        :return: object which can be used to cancel the subscription
        """

    # -----------------------------------------------------
    # pydantic 1
    @classmethod
    def parse_obj(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_raw(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def parse_file(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def from_orm(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    # -----------------------------------------------------
    # pydantic 2
    @classmethod
    def model_validate_strings(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()

    @classmethod
    def model_validate_json(cls, *args: Any, **kwargs: Any) -> NoReturn:
        raise FunctionCallNotAllowedError()
