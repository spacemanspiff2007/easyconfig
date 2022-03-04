from pathlib import Path
from typing import Optional, Union

from pydantic import PrivateAttr

from easyconfig.config_obj import PARENT_ROOT
from easyconfig.models import PathModel
from easyconfig.yaml import CommentedMap, write_aligned_yaml, yaml_rt


class AppConfigModel(PathModel):
    _ec_path: Optional[Path] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)

        self._easyconfig_initialize()
        self._easyconfig.parent = PARENT_ROOT
        # If data is empty it's the first creation of the object.
        self._easyconfig.parse_model(set_default_value=True if not data else False)

        self._ec_path: Optional[Path] = None

    def set_file_path(self, path: Union[Path, str]):
        """Set the path to the configuration file.
        If no file extension is specified ``.yml`` will be automatically appended.

        :param path: Path obj or str
        """
        if isinstance(path, str):
            path = Path(path)
        if not isinstance(path, Path):
            raise RuntimeError(f'Path to configuration file not specified: {path}')

        self._ec_path = path.resolve()
        if self._ec_path.suffix == '':
            self._ec_path = self._ec_path.with_name(self._ec_path.name + '.yml')

        super().set_file_path(self._ec_path.parent)

    def load_dict(self, obj: dict) -> bool:
        """Load values from a dictionary

        :param obj: dictionary containing all the keys
        :returns: True if config changed else False
        """
        return self._easyconfig.set_values(self.__class__(**obj))

    def load_file(self, path: Union[Path, str] = None) -> bool:
        """Load values from the configuration file. If the file doesn't exist it will be created.
        Missing required config entries will also be created.

        :param path: if not already set a path instance to the config file
        :returns: True if config changed else False
        """
        if path is not None:
            self.set_file_path(path)
        assert isinstance(self._ec_path, Path)

        cfg = CommentedMap()

        if self._ec_path.is_file():
            create_file = False
            with self._ec_path.open('r', encoding='utf-8') as file:
                cfg = yaml_rt.load(file)
            if cfg is None:
                cfg = CommentedMap()
        else:
            create_file = True

        # validiate data and create the obj
        obj = self.__class__(**cfg)
        config_changed = self._easyconfig.set_values(obj)

        # write back changed config
        if config_changed or create_file:
            self._easyconfig.update_map(cfg, use_file_defaults=create_file)

            with self._ec_path.open('w', encoding='utf-8') as file:
                write_aligned_yaml(cfg, file)

        return config_changed
