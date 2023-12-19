import json
from pathlib import Path
from typing import Any
from .model import RemoteAsset


# TODO 使用`LocalAsset`
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
    def __init__(self, repo: str, branch: str = "master"):
        """
        :param repo: 仓库名，格式为 owner/repo
        """
        assert repo.count("/") == 1
        self.__repo = repo
        self.__branch = branch

    def __str__(self) -> str:
        return f"https://github.com/{self.__repo}"

    def __truediv__(self, path: str) -> RemoteAsset:
        return RemoteAsset(
            f"https://raw.githubusercontent.com/{self.__repo}/{self.__branch}/{path}"
        )

    def __call__(self, path: str) -> str:
        return f"https://raw.githubusercontent.com/{self.__repo}/{self.__branch}/{path}"
