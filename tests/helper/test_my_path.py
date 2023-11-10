from .my_path import Path


def test_my_path():
    # Test some path operations
    a = Path('a')
    b = a / 'c'
    b.with_name('d.txt')

    # Buffer creation
    Path()._create_buffer()

    # Test behavior
    obj = Path(does_exist=True)
    assert obj.is_file()

    obj = Path(does_exist=False)
    assert not obj.is_file()

    obj = Path(does_exist=False, initial_value='asdf')
    assert obj.read_text() == 'asdf'

    obj.write_text('ffff')
    assert obj.get_value() == 'ffff'
