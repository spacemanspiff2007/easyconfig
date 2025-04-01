import pydantic
import pydantic_settings
from pydantic import ConfigDict

from easyconfig.models import AppConfigMixin, ConfigMixin


class BaseModel(pydantic.BaseModel, ConfigMixin):   # type: ignore[misc]
    model_config = ConfigDict(extra='forbid', validate_default=True)


class AppBaseModel(pydantic.BaseModel, AppConfigMixin):     # type: ignore[misc]
    model_config = ConfigDict(extra='forbid', validate_default=True)


class BaseSettings(pydantic_settings.BaseSettings, ConfigMixin):    # type: ignore[misc]
    model_config = ConfigDict(extra='forbid', validate_default=True)


class AppBaseSettings(pydantic_settings.BaseSettings, AppConfigMixin):  # type: ignore[misc]
    model_config = ConfigDict(extra='forbid', validate_default=True)
