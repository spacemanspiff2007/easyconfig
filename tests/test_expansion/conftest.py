import pytest

from easyconfig.expansion import load_var as var_module


@pytest.fixture()
def envs(monkeypatch):
    env_dict = {}
    monkeypatch.setattr(var_module, 'environ', env_dict)
    return env_dict
