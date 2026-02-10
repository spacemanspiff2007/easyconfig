import inspect

import pytest

from easyconfig.config_objs import AppConfig, ConfigObj
from easyconfig.config_objs.app_config import AppConfigBase, AsyncAppConfig
from easyconfig.models import AppConfigMixin, AsyncAppConfigMixin, ConfigMixin


def assert_signatures_match(cls, ref_cls) -> None:
    if cls is ref_cls:
        return None

    for name, value in inspect.getmembers(cls):
        if name.startswith('_') or name == 'from_model':
            continue
        impl = getattr(ref_cls, name)

        if isinstance(value, property):
            assert value.fset is None
            assert value.fdel is None
            value = value.fget
        if isinstance(impl, property):
            assert impl.fset is None
            assert impl.fdel is None
            impl = impl.fget

        target_spec = inspect.getfullargspec(value)
        current_spec = inspect.getfullargspec(impl)

        assert current_spec == target_spec
        assert inspect.getdoc(value) == inspect.getdoc(impl)

    return None


def test_assert_signature():
    assert_signatures_match(ConfigObj, AsyncAppConfig)
    with pytest.raises(AttributeError):
        assert_signatures_match(AsyncAppConfig, ConfigObj)


def assert_same_coros(cls, ref_cls) -> None:
    if cls is ref_cls:
        return None

    for name, value in inspect.getmembers(cls):
        if name.startswith('_') or name == 'from_model':
            continue

        impl = getattr(ref_cls, name)
        assert inspect.iscoroutinefunction(value) == inspect.iscoroutinefunction(impl)

    return None


def test_assert_same_coros():
    assert_signatures_match(ConfigObj, AppConfig)
    with pytest.raises(AssertionError):
        assert_same_coros(AsyncAppConfig, AppConfig)


@pytest.mark.parametrize(
    'cls', (AppConfig, AppConfigMixin, AsyncAppConfig, AsyncAppConfigMixin, ConfigObj, ConfigMixin))
@pytest.mark.parametrize('ref_cls', (AppConfig, AppConfigMixin, AsyncAppConfig, AsyncAppConfigMixin))
def test_signatures(cls, ref_cls) -> None:
    assert_signatures_match(cls, ref_cls)


@pytest.mark.parametrize('cls', (ConfigMixin, ConfigObj))
@pytest.mark.parametrize('ref_cls', (ConfigMixin, ConfigObj))
def test_signatures_2(cls, ref_cls) -> None:
    assert_signatures_match(cls, ref_cls)


@pytest.mark.parametrize('cls', (AppConfig, AppConfigMixin))
@pytest.mark.parametrize('ref_cls', (AppConfig, AppConfigMixin))
def test_signature_coros(cls, ref_cls) -> None:
    assert_same_coros(cls, ref_cls)


@pytest.mark.parametrize('cls', (ConfigMixin, ConfigObj))
@pytest.mark.parametrize('ref_cls', (ConfigMixin, ConfigObj))
def test_signature_coros_2(cls, ref_cls) -> None:
    assert_same_coros(cls, ref_cls)


@pytest.mark.parametrize('cls', (AppConfig, AppConfigMixin))
@pytest.mark.parametrize('ref_cls', (AppConfigMixin, AppConfig))
def test_signature_coros_3(cls, ref_cls) -> None:
    assert_same_coros(cls, ref_cls)


@pytest.mark.parametrize('cls', (AppConfig, AsyncAppConfig))
def test_init_matches(cls) -> None:
    target_spec = inspect.getfullargspec(AppConfigBase)
    current_spec = inspect.getfullargspec(cls)

    assert current_spec == target_spec
