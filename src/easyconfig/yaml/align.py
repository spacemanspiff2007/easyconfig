from io import BytesIO
from typing import Union

from easyconfig.yaml import yaml_rt


def align_comments(d, extra_indent=0):

    # Only process when it's a data structure -> dict or list
    is_dict = isinstance(d, dict)
    if not is_dict and not isinstance(d, list):
        return None

    comments = d.ca.items.values()
    if comments:
        max_col = max(map(lambda x: x[2].column, comments), default=0)
        indent_value = max_col + extra_indent
        for comment in comments:
            token = comment[2]
            token.column = indent_value

            # workaround for multiline eol comments
            if '\n' in token.value:
                c_lines = token.value.splitlines()  # type: list[str]
                for i, line in enumerate(c_lines):
                    # first line is automatically indendet correctly
                    if not i:
                        continue

                    _line = line.lstrip()
                    if _line:
                        c_lines[i] = indent_value * ' ' + _line
                token.value = '\n'.join(c_lines)

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
