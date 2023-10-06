from pathlib import Path

from . import config


class FileStorage:
    def __init__(self, name: str):
        self.__name = name
        self.__base_path = Path(config.canrot_config.canrot_data_path)

    def __call__(self, file_name: str) -> Path:
        return self.__base_path / self.__name / file_name

    def exists(self, file_name: str) -> bool:
        return self(file_name).exists()
