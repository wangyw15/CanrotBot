import json
import typing
from pathlib import Path

from .config import canrot_config

_base_data_path = Path(canrot_config.canrot_data_dir)
_dict_data: dict[str, dict[str, str]] = {}
_file_pointers: dict[Path, typing.IO] = {}
_DICT_FILE_NAME = '_dict.json'
_DEFAULT_DICT_NAME = '_default'


# 创建数据目录
_base_data_path.mkdir(parents=True, exist_ok=True)
# 加载数据
if (_base_data_path / _DICT_FILE_NAME).exists():
    _dict_data['_default'] = json.loads((_base_data_path / _DICT_FILE_NAME).read_text())
else:
    _dict_data['_default'] = {}
for i in _base_data_path.iterdir():
    if i.is_dir() and (i / _DICT_FILE_NAME).exists():
        _dict_data[i.name] = json.loads((i / _DICT_FILE_NAME).read_text())


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


def get_value(key: str, name: str = '') -> str:
    if not name:
        name = _DEFAULT_DICT_NAME
    return _dict_data[name][key]


def set_value(key: str, value: str,  name: str = '') -> None:
    if name:
        _dict_data[name][key] = value
    else:
        _dict_data[_DEFAULT_DICT_NAME][key] = value
    (_base_data_path / name / _DICT_FILE_NAME).write_text(
        json.dumps(_dict_data[name], ensure_ascii=False), encoding='utf-8')
