from typing import List

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.fields import FieldInfo


class MyDataSet:
    asdf = 'a'

    def __init__(self, parent) -> None:
        self.parent = parent


class MyModel(BaseModel):
    _my_data: MyDataSet = PrivateAttr()

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self._my_data = MyDataSet(self)


class UserModel(MyModel):
    val_int: int
    val_str: str = 'test'
    val_f: List[str] = Field(description='This key does this')


def test_get_model_desc() -> None:
    assert list(UserModel.model_fields.keys()) == [
        'val_int',
        'val_str',
        'val_f',
    ]

    for field in UserModel.model_fields.values():
        assert isinstance(field, FieldInfo)

    assert UserModel.model_fields['val_f'].description == 'This key does this'


def test_mutate(capsys) -> None:
    m = UserModel(val_int=1, val_f=['asdf'])

    assert isinstance(m, UserModel)
    assert isinstance(m._my_data, MyDataSet)
    assert m._my_data.parent == m

    # mutate to invalid data type
    m.val_int = 'asdf'
    assert m.val_int == 'asdf'

    # set attr
    setattr(m, 'val_int', 88)  # noqa: B010, RUF100
    assert m.val_int == 88

    for name in m.model_fields:
        print(f'{name}: {getattr(m, name)}')

    captured = capsys.readouterr()
    assert captured.out == "val_int: 88\nval_str: test\nval_f: ['asdf']\n"


def test_nested_models() -> None:
    class ChildModel(BaseModel):
        c_a: str = Field(3, description='desc c_a')
        c_b: int = Field(3, description='desc c_b')

    class ParentModel(BaseModel):
        a: str = Field(3, description='desc a')
        b: ChildModel = Field(default_factory=ChildModel, description='desc a')

    obj = ParentModel()
    assert obj.b.c_b == 3

    assert 'a' in obj.model_fields
    assert 'b' in obj.model_fields


def test_env_access() -> None:
    class ChildModel(BaseModel):
        c_a: str = Field(3, description='desc c_a', env='my_env_var')
        c_b: int = Field(3, description='desc c_b')

    class ParentModel(BaseModel):
        a: str = Field(3, description='desc a')
        b: ChildModel = Field(default_factory=ChildModel, description='desc a')

    obj = ParentModel()

    assert obj.b.model_fields['c_a'].json_schema_extra == {'env': 'my_env_var'}


def test_private_attr() -> None:
    class SimpleModel(BaseModel):
        _priv2: int = PrivateAttr(default=3)
        _priv3: int = PrivateAttr()
        a: int = 3

    SimpleModel()

    assert list(SimpleModel.model_fields.keys()) == [
        'a',
    ]
    assert list(SimpleModel.__private_attributes__.keys()) == ['_priv2', '_priv3']
