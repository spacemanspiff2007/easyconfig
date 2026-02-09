from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from typing_extensions import override

from easyconfig.__const__ import MISSING, MISSING_TYPE
from easyconfig.config_objs.object_config import ConfigObj
from easyconfig.errors import FileDefaultsNotSetError
from easyconfig.expansion import expand_obj
from easyconfig.pre_process import PreProcess
from easyconfig.yaml import CommentedMap, cmap_from_model, write_aligned_yaml, yaml_rt


if TYPE_CHECKING:
    from pydantic import BaseModel
    from typing_extensions import Self


class AppConfigBase(ConfigObj):
    def __init__(self, model: BaseModel, path: tuple[str, ...] = ('__root__',),
                 parent: MISSING_TYPE | Self = MISSING, file_defaults: BaseModel | None = None, **kwargs: Any) -> None:
        super().__init__(model, path, parent, **kwargs)

        self._file_defaults: Final = file_defaults
        self._preprocess: Final = PreProcess(self._file_defaults)
        self._file_path: Path | None = None

    @property
    def config_file_path(self) -> Path:
        """Path to the loaded configuration file"""

        if self._file_path is None:
            msg = 'No file path set'
            raise ValueError(msg)
        return self._file_path

    @property
    def load_preprocess(self) -> PreProcess:
        """A preprocessor which can be used to preprocess the configuration data before it is loaded"""
        return self._preprocess

    def set_file_path(self, path: Path | str) -> Self:
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

        return self

    def _update_from_dict(self, cfg: dict, *, expansion: bool = True) -> None:
        self._preprocess.run(cfg)

        if expansion:
            expand_obj(cfg)

        # validate data
        model_obj = self._obj_model_class.model_validate(cfg)

        # update mutable objects
        self._set_values(model_obj)

    def _read_create_file(self) -> CommentedMap:
        if self._file_path is None:
            msg = 'File path not set'
            raise ValueError(msg)

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

        return cfg

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

    def load_config_dict(self, cfg: dict, *, expansion: bool = True) -> Self:
        raise NotImplementedError()

    def load_config_file(self, path: Path | str | None = None, *, expansion: bool = True) -> Self:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self._file_path} at {id(self)}>'


class AppConfig(AppConfigBase):
    @override
    def load_config_dict(self, cfg: dict, *, expansion: bool = True) -> Self:
        """Load the configuration from a dictionary

        :param cfg: config dict which will be loaded
        :param expansion: Expand ${...} in strings
        """
        self._update_from_dict(cfg, expansion=expansion)
        return self

    @override
    def load_config_file(self, path: Path | str | None = None, *, expansion: bool = True) -> Self:
        """Load configuration from a yaml file. If the file does not exist a default file will be created

        :param path: Path to file
        :param expansion: Expand ${...} in strings
        """
        if path is not None:
            self.set_file_path(path)

        cfg = self._read_create_file()
        self.load_config_dict(cfg, expansion=expansion)
        return self


class AsyncAppConfig(AppConfigBase):
    @override
    async def load_config_dict(self, cfg: dict, *, expansion: bool = True) -> Self:
        """Load the configuration from a dictionary

        :param cfg: config dict which will be loaded
        :param expansion: Expand ${...} in strings
        """
        self._update_from_dict(cfg, expansion=expansion)
        return self

    @override
    async def load_config_file(self, path: Path | str | None = None, *, expansion: bool = True) -> Self:
        """Load configuration from a yaml file. If the file does not exist a default file will be created

        :param path: Path to file
        :param expansion: Expand ${...} in strings
        """
        if path is not None:
            self.set_file_path(path)

        cfg = self._read_create_file()
        await self.load_config_dict(cfg, expansion=expansion)
        return self
