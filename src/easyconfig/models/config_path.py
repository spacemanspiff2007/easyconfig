from pathlib import Path
from typing import Union

from easyconfig.models import ConfigModel


class PathModel(ConfigModel):

    def __init__(self, **data):
        super().__init__(**data)
        self._easyconfig.func_transform = self._transform_path

    def set_file_path(self, path: Union[Path, str]):
        """Set the file path for this PathModel and all sub PathModels.
        All path objects of of the model and all path objects of child PathModels that are relative
        will automatically be resolved relative the set path

        :param path: Path obj or str
        """
        if isinstance(path, str):
            path = Path(path)
        self._easyconfig.base_path = path.resolve()

    def _transform_path(self, new_value):
        if not isinstance(new_value, Path):
            return new_value

        if new_value.is_absolute():
            return new_value

        new_value = self._easyconfig.get_base_path() / new_value
        return new_value.resolve()
