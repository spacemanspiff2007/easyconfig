import pytest
from pydantic import BaseModel, Field, ValidationError

from easyconfig.config_objs import create_app_config


def test_simple():
    class SimpleModel(BaseModel):
        a: int = Field(5, alias='aaa')

    create_app_config(SimpleModel(aaa=99))
    create_app_config(SimpleModel(), {'aaa': 999})

    with pytest.raises(ValidationError):
        create_app_config(SimpleModel(), {'aaaa': 'asdf'})
