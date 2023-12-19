import json
from pathlib import Path
from typing import Any


class AssetManager:
    _asset_base_path = Path(__file__).parent.parent.parent / "assets"

    def __init__(self, asset_name: str):
        self.__base_path = self._asset_base_path / asset_name
        if not self.__base_path.exists() or not self.__base_path.is_dir():
            raise FileNotFoundError(f'Asset "{asset_name}" not found')

    def __call__(self, file_name: str = "") -> Path:
        return self.__base_path / file_name

    def __getitem__(self, file_name: str) -> Any | None:
        """
        读取对应路径的json文件

        :param file_name: 文件名，不需要后缀

        :return: 文件路径
        """
        path = self(file_name + ".json")
        if path.exists():
            with path.open("r", encoding="utf8") as f:
                return json.load(f)
        return None

    def __truediv__(self, other):
        return self.__base_path / other

    def __str__(self):
        return str(self.__base_path)

    def exists(self, file_name: str) -> bool:
        return self(file_name).exists()


class GithubAssetManager:
    # TODO 实现
    def __init__(self):
        pass
