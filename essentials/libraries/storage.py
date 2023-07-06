import json
import typing
from pathlib import Path

from .config import canrot_config

_T = typing.TypeVar('_T')
_base_data_path = Path(canrot_config.canrot_data_path)
# 创建数据目录
_base_data_path.mkdir(parents=True, exist_ok=True)


def get_base_path() -> Path:
    return _base_data_path


def get_path(name: str) -> Path:
    return _base_data_path / name


def write_json(name: str, obj: typing.Any):
    path = _base_data_path / f'{name}.json'
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=4, ensure_ascii=False), encoding='utf-8')


def load_json(name: str) -> typing.Any:
    return json.loads((_base_data_path / f'{name}.json').read_text(encoding='utf-8'))


class PersistentList(typing.MutableSequence[_T]):
    def __init__(self, file_name: str):
        self.__file_name: str = file_name
        self.__file_path: Path = _base_data_path / f'{file_name}.json'
        if self.__file_path.exists():
            self.__data = json.loads(self.__file_path.read_text(encoding='utf-8'))
        else:
            self.__data = []

    @property
    def path(self):
        return self.__file_path

    def insert(self, index: int, value: _T) -> None:
        self.__data.insert(index, value)
        self.save()

    @typing.overload
    def __getitem__(self, index: int) -> _T:
        return self.__data.__getitem__(index)

    @typing.overload
    def __getitem__(self, index: slice) -> typing.MutableSequence[_T]:
        return self.__data.__getitem__(index)

    def __getitem__(self, index: int) -> _T:
        return self.__data.__getitem__(index)

    def __setitem__(self, key: int, value: typing.Any):
        self.__data.__setitem__(key, value)
        self.save()

    def __delitem__(self, key: int):
        self.__data.__delitem__(key)
        self.save()

    def __len__(self) -> int:
        return self.__data.__len__()

    def save(self):
        self.__file_path.write_text(json.dumps(self.__data, indent=4, ensure_ascii=False), encoding='utf-8')


class PersistentData(typing.Generic[_T]):
    def __init__(self, storage_name: str):
        self.__storage_name: str = storage_name
        self.__data: dict[str] = {}
        self.__base_path: Path = get_path(self.__storage_name)
        # 自动创建文件夹
        if not self.__base_path.exists():
            self.__base_path.mkdir(parents=True, exist_ok=True)
        # 加载数据
        for i in get_path(self.__storage_name).iterdir():
            if i.is_file() and i.suffix == '.json':
                self.__data[i.stem] = json.loads(i.read_text(encoding='utf-8'))

    def _write(self, file_name: str, obj: _T):
        path = self.__base_path / f'{file_name}.json'
        path.write_text(json.dumps(obj, indent=4, ensure_ascii=False), encoding='utf-8')

    @property
    def storage_name(self):
        return self.__storage_name

    @property
    def data(self):
        return self.__data

    def __contains__(self, file_name: str):
        return file_name in self.__data

    def __getitem__(self, file_name: str) -> typing.Union[_T, None]:
        if file_name not in self.__data:
            return None
        return self.__data[file_name]

    def __setitem__(self, file_name: str, obj: _T):
        self.__data[file_name] = obj
        self._write(file_name, obj)

    def save(self):
        """
        保存所有数据
        """
        for file_name, data in self.__data.items():
            self._write(file_name, data)

    def open(self, file_name: str) -> typing.IO:
        """
        打开文件

        :param file_name: 文件名

        :return: 文件指针
        """
        path = self.__base_path / file_name
        return path.open('w+b')

    def exists(self, file_name: str) -> bool:
        """
        检查文件是否存在

        :param file_name: 文件名

        :return: 文件是否存在
        """
        return (self.__base_path / file_name).exists()
