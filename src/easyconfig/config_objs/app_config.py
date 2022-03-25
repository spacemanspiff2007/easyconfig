from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel, Extra
from typing_extensions import Self

from easyconfig.__const__ import MISSING, MISSING_TYPE
from .object_config import ConfigObj
from easyconfig.yaml import cmap_from_model, CommentedMap, write_aligned_yaml, yaml_rt


class AppConfig(ConfigObj):
    def __init__(self, model: BaseModel, path: Tuple[str, ...] = ('__root__',),
                 parent: Union[MISSING_TYPE, Self] = MISSING):
        super().__init__(model, path, parent)

        self._file_defaults: Optional[BaseModel] = None
        self._file_path: Optional[Path] = None

    def set_file_path(self, path: Union[Path, str]):
        if isinstance(path, str):
            path = Path(path)
        if not isinstance(path, Path):
            raise RuntimeError(f'Path to configuration file not specified: {path}')

        self._file_path = path.resolve()
        if not self._file_path.suffix:
            self._file_path = self._file_path.with_suffix('.yml')

    def load_config_dict(self, cfg: dict):
        # validate data
        model_obj = self._obj_model_class(**cfg)

        # update mutable objects
        self._set_values(model_obj)

    def load_config_file(self, path: Union[Path, str] = None):
        if path is not None:
            self.set_file_path(path)
        assert isinstance(self._file_path, Path)

        # create default config file
        if self._file_defaults is not None and not self._file_path.is_file():
            c_map = cmap_from_model(self._file_defaults)
            with self._file_path.open(mode='w', encoding='utf-8') as f:
                write_aligned_yaml(c_map, f, extra_indent=1)

        # Load data from file
        with self._file_path.open('r', encoding='utf-8') as file:
            cfg = yaml_rt.load(file)
        if cfg is None:
            cfg = CommentedMap()

        # load c_map data (which is a dict)
        self.load_config_dict(cfg)


TYPE_WRAPPED = TypeVar('TYPE_WRAPPED', bound=BaseModel)


def create_app_config(model: TYPE_WRAPPED,
                      file_values: Union[MISSING_TYPE, None, BaseModel, Dict[str, Any]] = MISSING,
                      validate_file_values=True) -> TYPE_WRAPPED:

    # Implicit default
    if file_values is MISSING:
        file_values = model

    # Validate default
    if file_values is not None:
        if isinstance(file_values, dict):
            if validate_file_values:
                class NoExtraEntries(model.__class__, extra=Extra.forbid):
                    pass
                NoExtraEntries.parse_obj(file_values)

            file_values = model.__class__.parse_obj(file_values)

    app_cfg = AppConfig.from_model(model)

    assert file_values is None or isinstance(file_values, BaseModel)
    app_cfg._file_defaults = file_values
    return app_cfg
