from __future__ import annotations

from typing import TYPE_CHECKING

from easyconfig.models.config import ConfigMixin

if TYPE_CHECKING:
    from pathlib import Path


class AppConfigMixin(ConfigMixin):
    def set_file_path(self, path: Path | str):
        """Set the path to the configuration file.
        If no file extension is specified ``.yml`` will be automatically appended.

        :param path: Path obj or str
        """

    def load_config_dict(self, cfg: dict, /, expansion: bool = True):
        """Load the configuration from a dictionary

        :param cfg: config dict which will be loaded
        :param expansion: Expand ${...} in strings
        """

    def load_config_file(self, path: Path | str | None = None, expansion: bool = True):
        """Load configuration from a yaml file. If the file does not exist a default file will be created

        :param path: Path to file
        :param expansion: Expand ${...} in strings
        """

    def generate_default_yaml(self) -> str:
        """Generate the default YAML structure

        :returns: YAML structure as a string
        """
