import os
from pathlib import Path

import pytest
from pydantic import Field

from easyconfig import PathModel


class SubModel(PathModel):
    p11 = Path('c:/sub1')
    p12 = Path('../sub2')


class MyPathModel(PathModel):
    p1 = Path('c:/folder1')
    p2 = Path('./folder2')

    sub: SubModel = Field(default_factory=SubModel)


@pytest.mark.skipif(os.name != 'nt', reason='relative path are different')
def test_path():
    m = MyPathModel()
    m._easyconfig.parse_model()
    m.set_file_path(Path('c:/folder'))
    m._easyconfig.set_values(MyPathModel())

    assert m.p1.as_posix().lower() == 'c:/folder1'
    assert m.p2.as_posix().lower() == 'c:/folder/folder2'
    assert m.sub.p11.as_posix().lower() == 'c:/sub1'
    assert m.sub.p12.as_posix().lower() == 'c:/sub2'
