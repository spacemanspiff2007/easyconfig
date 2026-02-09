from typing import Final
from unittest.mock import AsyncMock, Mock, call

import pytest
from pydantic import BaseModel

from easyconfig.config_objs import AppConfig
from easyconfig.config_objs.app_config import AsyncAppConfig
from easyconfig.models import ConfigMixin


def pytest_ids(obj):
    if not isinstance(obj, SubTestHelper):
        raise TypeError()
    return obj._app_cls.__name__


class SubTestHelper:
    def __init__(self, app_cls: type[AppConfig] | type[AsyncAppConfig]):
        self._app_cls: Final = app_cls
        self._mock_cls: Final = AsyncMock if app_cls is AsyncAppConfig else Mock

    def get_mock(self, name: str):
        return self._mock_cls(__name__=name)

    def from_model(self, obj: BaseModel) -> AppConfig | AsyncAppConfig:
        return self._app_cls.from_model(obj)

    async def load_config_dict(self, obj: AppConfig | AsyncAppConfig, value: dict):
        if self._app_cls is AsyncAppConfig:
            await obj.load_config_dict(value)
        else:
            obj.load_config_dict(value)


@pytest.mark.parametrize('helper', (SubTestHelper(AppConfig), SubTestHelper(AsyncAppConfig)), ids=pytest_ids)
def test_sub_name(helper) -> None:
    class SimpleModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    def my_func() -> None:
        pass

    o = helper.from_model(SimpleModel())
    sub = o.subscribe_for_changes(my_func)

    assert str(sub) == '<ConfigObjSubscription my_func @ __root__>'


@pytest.mark.parametrize('helper', (SubTestHelper(AppConfig), SubTestHelper(AsyncAppConfig)), ids=pytest_ids)
async def test_sub_simple(helper) -> None:
    class SimpleModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    m = helper.get_mock('my_mock')
    o = helper.from_model(SimpleModel())
    sub = o.subscribe_for_changes(m)

    m.assert_not_called()
    await helper.load_config_dict(o, {'a': 6})
    m.assert_called_once_with()

    sub.cancel()
    await helper.load_config_dict(o, {'a': 99})
    m.assert_called_once_with()


@pytest.mark.parametrize('helper', (SubTestHelper(AppConfig), SubTestHelper(AsyncAppConfig)), ids=pytest_ids)
async def test_sub_sub_no_propagate(helper) -> None:
    class SubModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    class SimpleModel(BaseModel, ConfigMixin):
        a: SubModel = SubModel()

    mock_child = helper.get_mock(name='sub_mock')
    mock_parent = helper.get_mock(name='parent_mock')

    o = helper.from_model(SimpleModel())
    sub_child = o.a.subscribe_for_changes(mock_child)
    sub_parent = o.subscribe_for_changes(mock_parent)

    mock_child.assert_not_called()
    mock_parent.assert_not_called()

    await helper.load_config_dict(o, {'a': {'a': 9}})
    mock_child.assert_called_once_with()
    mock_parent.assert_not_called()

    # Cancel child sub - should now be propagated to parent
    sub_child.cancel()

    await helper.load_config_dict(o, {'a': {'a': 10}})
    mock_child.assert_called_once_with()
    mock_parent.assert_called_once_with()

    sub_parent.cancel()


@pytest.mark.parametrize('helper', (SubTestHelper(AppConfig), SubTestHelper(AsyncAppConfig)), ids=pytest_ids)
async def test_sub_sub_propagate(helper) -> None:
    class SubModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    class SimpleModel(BaseModel, ConfigMixin):
        a: SubModel = SubModel()

    mock_child = helper.get_mock(name='sub_mock')
    mock_parent = helper.get_mock(name='parent_mock')

    o = helper.from_model(SimpleModel())
    sub_child = o.a.subscribe_set_options(propagate=True).subscribe_for_changes(mock_child)
    sub_parent = o.subscribe_for_changes(mock_parent)

    mock_child.assert_not_called()
    mock_parent.assert_not_called()

    await helper.load_config_dict(o, {'a': {'a': 9}})
    mock_child.assert_called_once_with()
    mock_parent.assert_called_once_with()

    # Cancel child sub - should now still be propagated to parent
    sub_child.cancel()

    await helper.load_config_dict(o, {'a': {'a': 10}})
    mock_child.assert_called_once_with()
    mock_parent.assert_has_calls([call(), call()])

    sub_parent.cancel()
