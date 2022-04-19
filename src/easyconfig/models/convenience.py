import pydantic

from easyconfig.models import AppConfigMixin, ConfigMixin


class BaseModel(pydantic.BaseModel, ConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid
        validate_all = True


class AppBaseModel(pydantic.BaseModel, AppConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid
        validate_all = True


class BaseSettings(pydantic.BaseSettings, ConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid
        validate_all = True


class AppBaseSettings(pydantic.BaseSettings, AppConfigMixin):

    class Config:
        extra = pydantic.Extra.forbid
        validate_all = True
