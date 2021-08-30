import io

from easyconfig.yaml import yaml_rt as yaml


def dump_yaml(obj) -> str:
    tmp = io.StringIO()
    yaml.dump(obj, tmp)
    return tmp.getvalue()
