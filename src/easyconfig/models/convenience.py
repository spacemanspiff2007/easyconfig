import pydantic

from easyconfig.models import AppConfigMixin, ConfigMixin


class BaseModel(pydantic.BaseModel, ConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid


class AppBaseModel(pydantic.BaseModel, AppConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid


class BaseSettings(pydantic.BaseSettings, ConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid


class AppBaseSettings(pydantic.BaseSettings, AppConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid
