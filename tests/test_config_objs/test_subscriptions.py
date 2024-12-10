from unittest.mock import Mock, call

from pydantic import BaseModel

from easyconfig.config_objs import ConfigObj
from easyconfig.models import ConfigMixin


def test_sub_name() -> None:
    class SimpleModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    def my_func() -> None:
        pass

    o = ConfigObj.from_model(SimpleModel())
    sub = o.subscribe_for_changes(my_func)

    assert str(sub) == '<ConfigObjSubscription my_func @ __root__>'


def test_sub_simple() -> None:
    class SimpleModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    m = Mock(__name__='Mock')

    o = ConfigObj.from_model(SimpleModel())
    sub = o.subscribe_for_changes(m)

    m.assert_not_called()
    o._set_values(SimpleModel(a=6))
    m.assert_called_once_with()

    sub.cancel()
    o._set_values(SimpleModel(a=99))
    m.assert_called_once_with()


def test_sub_sub_no_propagate() -> None:
    class SubModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    class SimpleModel(BaseModel, ConfigMixin):
        a: SubModel = SubModel()

    mock_child = Mock(__name__='sub_mock')
    mock_parent = Mock(__name__='parent_mock')

    o = ConfigObj.from_model(SimpleModel())
    sub_child = o.a.subscribe_for_changes(mock_child, on_next_load=False)
    sub_parent = o.subscribe_for_changes(mock_parent, on_next_load=False)

    mock_child.assert_not_called()
    mock_parent.assert_not_called()

    o._set_values(SimpleModel(a=SubModel(a=9)))
    mock_child.assert_called_once_with()
    mock_parent.assert_not_called()

    # Cancel child sub - should now be propagated to parent
    sub_child.cancel()

    o._set_values(SimpleModel(a=SubModel(a=10)))
    mock_child.assert_called_once_with()
    mock_parent.assert_called_once_with()

    sub_parent.cancel()


def test_sub_sub_propagate() -> None:
    class SubModel(BaseModel, ConfigMixin):
        a: int = 5
        b: int = 6

    class SimpleModel(BaseModel, ConfigMixin):
        a: SubModel = SubModel()

    mock_child = Mock(__name__='sub_mock')
    mock_parent = Mock(__name__='parent_mock')

    o = ConfigObj.from_model(SimpleModel())
    sub_child = o.a.subscribe_for_changes(mock_child, propagate=True)
    sub_parent = o.subscribe_for_changes(mock_parent)

    mock_child.assert_not_called()
    mock_parent.assert_not_called()

    o._set_values(SimpleModel(a=SubModel(a=9)))
    mock_child.assert_called_once_with()
    mock_parent.assert_called_once_with()

    # Cancel child sub - should now still be propagated to parent
    sub_child.cancel()

    o._set_values(SimpleModel(a=SubModel(a=10)))
    mock_child.assert_called_once_with()
    mock_parent.assert_has_calls([call(), call()])

    sub_parent.cancel()
