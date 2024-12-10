import inspect

import pytest

from easyconfig.config_objs import AppConfig, ConfigObj
from easyconfig.models import AppConfigMixin, ConfigMixin


@pytest.mark.parametrize(
    ('mixin_cls', 'impl_cls'),
    [
        (AppConfigMixin, AppConfig),
        (AppConfig, AppConfigMixin),
        (ConfigMixin, ConfigObj),
        (ConfigObj, ConfigMixin),
    ],
)
def test_signatures_match(mixin_cls, impl_cls) -> None:
    """Ensure that the mixin and the implementation have the same signatures"""

    for name, value in inspect.getmembers(mixin_cls):
        if name.startswith('_') or name in ('from_model',):
            continue
        impl = getattr(impl_cls, name)

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
