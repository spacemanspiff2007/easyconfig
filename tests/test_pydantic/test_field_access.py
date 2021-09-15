from typing import List

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.fields import ModelField


class MyDataSet:
    asdf = 'a'

    def __init__(self, parent):
        self.parent = parent


class MyModel(BaseModel):
    _my_data: MyDataSet = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._my_data = MyDataSet(self)


class UserModel(MyModel):
    val_int: int
    val_str = 'test'
    val_f: List[str] = Field(description='This key does this')


def test_get_model_desc():

    assert list(UserModel.__fields__.keys()) == ['val_int', 'val_f', 'val_str', ]

    for field in UserModel.__fields__.values():
        assert isinstance(field, ModelField)


def test_mutate(capsys):
    m = UserModel(val_int=1, val_f=['asdf'])

    assert isinstance(m, UserModel)
    assert isinstance(m._my_data, MyDataSet)
    assert m._my_data.parent == m

    # mutate to invalid data type
    m.val_int = 'asdf'
    assert m.val_int == 'asdf'

    # set attr
    setattr(m, 'val_int', 88)
    assert m.val_int == 88

    for name in m.__fields__:
        print(f'{name}: {getattr(m, name)}')

    captured = capsys.readouterr()
    assert captured.out == "val_int: 88\nval_f: ['asdf']\nval_str: test\n"


def test_nested_models():

    class ChildModel(BaseModel):
        c_a: str = Field(3, description='desc c_a')
        c_b: int = Field(3, description='desc c_b')

    class ParentModel(BaseModel):
        a: str = Field(3, description='desc a')
        b: ChildModel = Field(default_factory=ChildModel, description='desc a')

    obj = ParentModel()
    assert obj.b.c_b == 3

    assert 'a' in obj.__fields__
    assert 'b' in obj.__fields__


def test_env_access():

    class ChildModel(BaseModel):
        c_a: str = Field(3, description='desc c_a', env='my_env_var')
        c_b: int = Field(3, description='desc c_b')

    class ParentModel(BaseModel):
        a: str = Field(3, description='desc a')
        b: ChildModel = Field(default_factory=ChildModel, description='desc a')

    obj = ParentModel()
    assert obj.b.c_b == 3

    assert 'a' in obj.__fields__
    assert 'b' in obj.__fields__
