import inspect

import pytest

from easyconfig.config_objs import AppConfig, ConfigObj
from easyconfig.models import AppConfigMixin, ConfigMixin


@pytest.mark.parametrize(
    'mixin_cls, impl_cls', ((AppConfigMixin, AppConfig), (AppConfig, AppConfigMixin),
                            (ConfigMixin, ConfigObj), (ConfigObj, ConfigMixin), ))
def test_signatures_match(mixin_cls, impl_cls):
    """Ensure that the mixin and the implementation have the same signatures"""

    for name, value in inspect.getmembers(mixin_cls):
        if name.startswith('_') or name in ('from_model', ):
            continue

        impl = getattr(impl_cls, name)

        target_spec = inspect.getfullargspec(value)
        current_spec = inspect.getfullargspec(impl)

        assert current_spec == target_spec
