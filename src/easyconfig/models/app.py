from pathlib import Path
from typing import Union

from easyconfig.models.config import ConfigMixin


class AppConfigMixin(ConfigMixin):

    def set_file_path(self, path: Union[Path, str]):
        """Set the path to the configuration file.
        If no file extension is specified ``.yml`` will be automatically appended.

        :param path: Path obj or str
        """
        pass

    def load_config_dict(self, cfg: dict):
        """Load values from a dictionary

        :param cfg: dictionary containing all the keys
        :returns: True if config changed else False
        """
        pass

    def load_config_file(self, path: Union[Path, str] = None):
        """Load values from the configuration file. If the file doesn't exist it will be created.
        Missing required config entries will also be created.

        :param path: if not already set a path instance to the config file
        :returns: True if config changed else False
        """
        pass
