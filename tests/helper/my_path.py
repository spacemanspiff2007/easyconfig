from io import StringIO, TextIOWrapper
from pathlib import Path as _Path
from typing import Optional
from sys import version_info

_path_type = type(_Path())


class Path(_path_type):
    if version_info < (3, 12):
        _flavour = _path_type._flavour

        def __init__(self, *args, does_exist: bool = True, initial_value: Optional[str] = None, **kwargs):
            super().__init__()

            if hasattr(Path, '_from_parts'):
                Path._from_parts(args)
            else:
                # Pathlib init
                drv, root, parts = self._parse_args(args)
                self._drv = drv
                self._root = root
                self._parts = parts
                self._init()

            # Own Path implementation
            self.does_exist: bool = does_exist
            self.contents = None
            self._create_buffer(initial_value)

        def __new__(cls, *args, **kwargs):
            return super().__new__(cls, *args)

    else:
        def __init__(self, *args, does_exist: bool = True, initial_value: Optional[str] = None, **kwargs):
            super().__init__()
            # Own Path implementation
            self.does_exist: bool = does_exist
            self.contents = None
            self._create_buffer(initial_value)

    def _create_buffer(self, initial_value: Optional[str] = None):
        self.contents = StringIO(initial_value)
        self.contents.close = lambda: None

    def is_file(self) -> bool:
        return self.does_exist

    def get_value(self) -> str:
        return self.contents.getvalue()

    def open(self, *args, mode='r', **kwargs) -> TextIOWrapper:
        if 'w' in mode and 'a' not in mode:
            self._create_buffer()
        return self.contents

    def resolve(self):
        return self
