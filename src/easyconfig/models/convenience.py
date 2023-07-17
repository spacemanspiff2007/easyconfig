import pydantic
import pydantic_settings
from pydantic import ConfigDict

from easyconfig.models import AppConfigMixin, ConfigMixin


class BaseModel(pydantic.BaseModel, ConfigMixin):
    model_config = ConfigDict(extra='forbid', validate_default=True)


class AppBaseModel(pydantic.BaseModel, AppConfigMixin):
    model_config = ConfigDict(extra='forbid', validate_default=True)


class BaseSettings(pydantic_settings.BaseSettings, ConfigMixin):
    model_config = ConfigDict(extra='forbid', validate_default=True)


class AppBaseSettings(pydantic_settings.BaseSettings, AppConfigMixin):
    model_config = ConfigDict(extra='forbid', validate_default=True)
