from typing import Dict, Optional

from pydantic import Field

from easyconfig import AppConfigModel, ConfigModel
from helper import Path

# def test_load_simple():
#     class SubModel(ConfigModel):
#         a: str = None
#
#     class MyTestModel(ConfigModel):
#         sub: SubModel = Field(default_factory=lambda: SubModel(a='test'), alias='b')
#
#     class MyCfg(AppConfigModel):
#         name: MyTestModel = MyTestModel()
#
#     p = Path('testfile.yml', does_exist=False)
#
#     config = MyCfg()
#     assert config.name.sub.a == 'test'
#
#     config.load_file(p)
#
#     file = p.contents.getvalue()
#     assert file == 'name:\n  b:\n    a: test\n'
#
#
# def test_create_default():
#
#     class SubModel(ConfigModel):
#         sub_int: int = Field(0, file_value=5)
#         sub_opt: Optional[str] = Field('', file_value='asdf')
#
#     class MyCfg(AppConfigModel):
#         name: SubModel = SubModel()
#
#     p = Path('testfile.yml', does_exist=False)
#
#     config = MyCfg()
#     assert config.name.sub_int == 0
#     assert config.name.sub_opt == ''
#
#     config.load_file(p)
#
#     file = p.contents.getvalue()
#     assert file == 'name:\n  sub_int: 5\n  sub_opt: asdf\n'


def test_parse_multiple_sub_sub_models():

    class SubSubCfg(ConfigModel):
        ssa: int = None
        ssb: int = Field(5, file_value=10)

    class SubCfg(ConfigModel):
        sa: SubSubCfg = Field(SubSubCfg(), file_value=SubSubCfg())
        sb: SubSubCfg = Field(SubSubCfg(), file_value=SubSubCfg(ssb=3))

    class MyCfg(AppConfigModel):
        a: Optional[Dict[str, SubCfg]] = Field(None, file_value={'key': SubCfg(sa=SubSubCfg(ssa=8))})

    p = Path('testfile.yml', does_exist=False)

    config = MyCfg()
    config.load_file(p)

    file = p.contents.getvalue()
    assert file == 'a:\n' \
                   '  key:\n' \
                   '    sa:\n' \
                   '      ssa: 8\n' \
                   '      ssb: 5\n' \
                   '    sb:\n' \
                   '      ssb: 5\n'
