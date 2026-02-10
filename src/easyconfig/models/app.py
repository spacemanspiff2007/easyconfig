from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from easyconfig.models.config import ConfigMixin


if TYPE_CHECKING:
    from pathlib import Path

    from easyconfig.pre_process import PreProcess


class AppConfigMixin(ConfigMixin):
    @property
    def config_file_path(self) -> Path:
        """Path to the loaded configuration file"""

    @property
    def load_preprocess(self) -> PreProcess:
        """A preprocessor which can be used to preprocess the configuration data before it is loaded"""

    def set_file_path(self, path: Path | str) -> Self:
        """Set the path to the configuration file.
        If no file extension is specified ``.yml`` will be automatically appended.

        :param path: Path obj or str
        """

    def load_config_dict(self, cfg: dict, *, expansion: bool = True) -> Self:
        """Load the configuration from a dictionary

        :param cfg: config dict which will be loaded
        :param expansion: Expand ${...} in strings
        """

    def load_config_file(self, path: Path | str | None = None, *, expansion: bool = True) -> Self:
        """Load configuration from a yaml file. If the file does not exist a default file will be created

        :param path: Path to file
        :param expansion: Expand ${...} in strings
        """

    def generate_default_yaml(self) -> str:
        """Generate the default YAML structure

        :returns: YAML structure as a string
        """


class AsyncAppConfigMixin(ConfigMixin):
    @property
    def config_file_path(self) -> Path:
        """Path to the loaded configuration file"""

    @property
    def load_preprocess(self) -> PreProcess:
        """A preprocessor which can be used to preprocess the configuration data before it is loaded"""

    def set_file_path(self, path: Path | str) -> Self:
        """Set the path to the configuration file.
        If no file extension is specified ``.yml`` will be automatically appended.

        :param path: Path obj or str
        """

    async def load_config_dict(self, cfg: dict, *, expansion: bool = True) -> Self:
        """Load the configuration from a dictionary

        :param cfg: config dict which will be loaded
        :param expansion: Expand ${...} in strings
        """

    async def load_config_file(self, path: Path | str | None = None, *, expansion: bool = True) -> Self:
        """Load configuration from a yaml file. If the file does not exist a default file will be created

        :param path: Path to file
        :param expansion: Expand ${...} in strings
        """

    def generate_default_yaml(self) -> str:
        """Generate the default YAML structure

        :returns: YAML structure as a string
        """
