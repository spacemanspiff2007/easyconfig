from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

from ..errors import FileDefaultsNotSetError
from .object_config import ConfigObj
from easyconfig.__const__ import MISSING, MISSING_TYPE
from easyconfig.expansion import expand_obj
from easyconfig.yaml import CommentedMap, cmap_from_model, write_aligned_yaml, yaml_rt

if TYPE_CHECKING:
    from pydantic import BaseModel
    from typing_extensions import Self


class AppConfig(ConfigObj):
    def __init__(self, model: BaseModel, path: tuple[str, ...] = ('__root__',), parent: MISSING_TYPE | Self = MISSING):
        super().__init__(model, path, parent)

        self._file_defaults: BaseModel | None = None
        self._file_path: Path | None = None

    def set_file_path(self, path: Path | str):
        """Set the path to the configuration file.
        If no file extension is specified ``.yml`` will be automatically appended.

        :param path: Path obj or str
        """
        if isinstance(path, str):
            path = Path(path)
        if not isinstance(path, Path):
            msg = f'Path to configuration file not of type Path: {path} ({type(path)})'
            raise TypeError(msg)

        self._file_path = path.resolve()
        if not self._file_path.suffix:
            self._file_path = self._file_path.with_suffix('.yml')

    def load_config_dict(self, cfg: dict, /, expansion: bool = True):
        """Load the configuration from a dictionary

        :param cfg: config dict which will be loaded
        :param expansion: Expand ${...} in strings
        """
        if expansion:
            expand_obj(cfg)

        # validate data
        model_obj = self._obj_model_class(**cfg)

        # update mutable objects
        self._set_values(model_obj)
        return self

    def load_config_file(self, path: Path | str | None = None, expansion: bool = True):
        """Load configuration from a yaml file. If the file does not exist a default file will be created

        :param path: Path to file
        :param expansion: Expand ${...} in strings
        """
        if path is not None:
            self.set_file_path(path)
        assert isinstance(self._file_path, Path)

        # create default config file
        if self._file_defaults is not None and not self._file_path.is_file():
            __yaml = self.generate_default_yaml()
            with self._file_path.open(mode='w', encoding='utf-8') as f:
                f.write(__yaml)

        # Load data from file
        with self._file_path.open('r', encoding='utf-8') as file:
            cfg = yaml_rt.load(file)
        if cfg is None:
            cfg = CommentedMap()

        # load c_map data (which is a dict)
        self.load_config_dict(cfg, expansion=expansion)
        return self

    def generate_default_yaml(self) -> str:
        """Generate the default YAML structure

        :returns: YAML structure as a string
        """
        if self._file_defaults is None:
            raise FileDefaultsNotSetError()

        buffer = StringIO()
        c_map = cmap_from_model(self._file_defaults)
        write_aligned_yaml(c_map, buffer, extra_indent=1)
        return buffer.getvalue()
