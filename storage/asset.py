import json
import typing
from pathlib import Path

_asset_base_path = Path(__file__).parent.parent / 'assets'


def get_assets_base_path() -> Path:
    return _asset_base_path


def get_assets_path(asset_name: str) -> Path:
    return _asset_base_path / asset_name


def load_json(file_name: str) -> typing.Any:
    with (_asset_base_path / file_name).open(encoding='utf-8') as f:
        return json.load(f)


class Asset:
    def __init__(self, asset_name: str):
        self.__base_path = _asset_base_path / asset_name
        if not self.__base_path.exists() or not self.__base_path.is_dir():
            raise FileNotFoundError(f'Asset "{asset_name}" not found')
        # 自动加载json文件
        self.__data: dict[str] = {}
        for i in self.__base_path.glob('*.json'):
            if i.is_file():
                self.__data[i.stem] = json.loads(i.read_text(encoding='utf8'))

    def __call__(self, file_name: str = '') -> Path:
        return self.__base_path / file_name

    def __getitem__(self, key: str):
        return self.__data[key]

    def exists(self, file_name: str) -> bool:
        return self(file_name).exists()

    def items(self):
        return self.__data.items()

    def open(self, file_name: str, *args, **kwargs) -> typing.IO:
        return (self.__base_path / file_name).open(*args, **kwargs)

