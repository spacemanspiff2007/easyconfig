import io

import pytest

from easyconfig.yaml import CommentedMap, write_aligned_yaml, yaml_rt


@pytest.fixture
def my_map():
    top = CommentedMap()
    top['sub_key1'] = data = CommentedMap()

    # this is currently not supported, but we should not crash if a user does this
    top.yaml_set_comment_before_after_key('sub_key1', before='my description')

    data['a'] = 1
    data['b'] = 'asdf'
    data['c'] = 3.3333
    data.yaml_add_eol_comment('comment 1', 'a')
    data.yaml_add_eol_comment('comment 2', 'b')
    data.yaml_add_eol_comment('comment 3', 'c')

    top['sub_key2'] = data = CommentedMap()

    data['a'] = 'long text'
    data['b'] = 'an even longer text'
    data.yaml_add_eol_comment('comment 4', 'a')
    data.yaml_add_eol_comment('comment 5', 'b')

    data['c'] = sub = CommentedMap()
    data.yaml_add_eol_comment('c', 'my description 2')

    sub['a'] = 'long text'
    sub['b'] = 'an even longer text'
    sub.yaml_add_eol_comment('comment 4', 'a')
    sub.yaml_add_eol_comment('comment 5', 'b')

    top['sub_key3'] = data = CommentedMap()
    data['a'] = 'long text'
    data.yaml_add_eol_comment('# This is a multiline\n# comment', 'a')
    data['b'] = 'another long text'
    data.yaml_add_eol_comment('#\n# Another\n\n# comment', 'b')

    return top


def test_align(my_map: CommentedMap) -> None:
    buf = io.StringIO()
    write_aligned_yaml(my_map, buf, 1)
    file_contents = buf.getvalue()

    assert file_contents == '''# my description
sub_key1:
  a: 1       # comment 1
  b: asdf    # comment 2
  c: 3.3333  # comment 3
sub_key2:
  a: long text            # comment 4
  b: an even longer text  # comment 5
  c:
    a: long text            # comment 4
    b: an even longer text  # comment 5
sub_key3:
  a: long text          # This is a multiline
                        # comment
  b: another long text  #
                        # Another

                        # comment
'''

    top = yaml_rt.load(io.StringIO(initial_value=file_contents))
    buf = io.StringIO()
    write_aligned_yaml(top, buf)
    assert file_contents == buf.getvalue()
