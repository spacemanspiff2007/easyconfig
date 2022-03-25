from io import BytesIO
from typing import Union

from easyconfig.yaml import yaml_rt


def align_comments(d, extra_indent=0):

    # Only process when its a data structure -> dict or list
    is_dict = isinstance(d, dict)
    if not is_dict and not isinstance(d, list):
        return None

    comments = d.ca.items.values()
    if comments:
        max_col = max(map(lambda x: x[2].column, comments), default=0)
        for comment in comments:
            comment[2].column = max_col + extra_indent

    for element in (d.values() if is_dict else d):
        align_comments(element, extra_indent=extra_indent)
    return None


def remove_none(obj: Union[dict]):
    rem = []
    for index, value in obj.items():
        if isinstance(value, dict):
            remove_none(value)
            if not value:
                rem.append(index)
        else:
            if value is None:
                rem.append(index)

    for k in rem:
        obj.pop(k)


def write_aligned_yaml(obj, file_obj, extra_indent: int = 0):
    assert extra_indent >= 0, extra_indent

    buffer = BytesIO()
    yaml_rt.dump(obj, buffer)

    loaded_obj = yaml_rt.load(buffer.getvalue())
    remove_none(loaded_obj)
    align_comments(loaded_obj, extra_indent)

    yaml_rt.dump(loaded_obj, file_obj)
    return None
