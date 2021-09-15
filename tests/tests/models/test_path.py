import os
from pathlib import Path

import pytest
from pydantic import Field

from easyconfig import PathModel


@pytest.mark.skipif(os.name != 'nt', reason='relative path symbols are different')
def test_path():

    class SubModel(PathModel):
        p11 = Path('c:/sub1')
        p12 = Path('../sub2')

    class MyPathModel(PathModel):
        p1 = Path('c:/folder1')
        p2 = Path('./folder2')

        sub: SubModel = Field(default_factory=SubModel)

    m = MyPathModel()
    m._easyconfig_initialize().parse_model()
    m.set_file_path(Path('c:/folder'))

    defaults = MyPathModel()

    m._easyconfig.set_values(defaults)

    assert m.p1.as_posix().lower() == 'c:/folder1'
    assert m.p2.as_posix().lower() == 'c:/folder/folder2'
    assert m.sub.p11.as_posix().lower() == 'c:/sub1'
    assert m.sub.p12.as_posix().lower() == 'c:/sub2'


@pytest.mark.skipif(os.name != 'nt', reason='relative path symbols are different')
def test_str_to_path():
    class MyPathModel(PathModel):
        p: Path = Field('c:/folder1')

    m = MyPathModel()
    m._easyconfig_initialize().parse_model()
    m._easyconfig.set_values(MyPathModel())

    assert isinstance(m.p, Path)
    assert str(m.p) == 'c:\\folder1'
