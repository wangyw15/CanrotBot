from pathlib import Path

from . import config


class FileStorage:
    def __init__(self, name: str):
        self.__base_path = Path(config.global_config.data_path) / name
        if not self.__base_path.exists():
            self.__base_path.mkdir(parents=True)

    def __call__(self, file_name: str) -> Path:
        ret = self.__base_path / file_name
        if not ret.parent.exists():
            ret.parent.mkdir(parents=True)
        return ret

    def exists(self, file_name: str) -> bool:
        return self(file_name).exists()
