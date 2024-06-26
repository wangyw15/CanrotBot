import abc
import json
from datetime import datetime, timedelta
from hashlib import md5
from pathlib import Path
from typing import Any

from httpx import Client
from sqlalchemy import select, update, insert

from storage import config, database
from . import data

_client = Client(proxy=config.canrot_config.canrot_proxy)


class Asset(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def json(self) -> dict:
        pass

    @abc.abstractmethod
    def text(self) -> str:
        pass

    @abc.abstractmethod
    def raw(self) -> bytes:
        pass


class RemoteAsset(Asset):
    _cache_path = Path(config.canrot_config.canrot_data_path) / "cache/asset"

    def __init__(
        self, url: str, expire: datetime | timedelta | None = None, key: str = ""
    ):
        self.__url = url

        if key:
            self.__key = key
        else:
            self.__key = self.generate_key(url)

        self.__expire = expire

        if not self._cache_path.exists():
            self._cache_path.mkdir(parents=True)

        if (self._cache_path / self.__key).exists():
            self.__data: bytes | None = (self._cache_path / self.__key).read_bytes()
        else:
            self.__data: bytes | None = None

    @staticmethod
    def generate_key(url: str) -> str:
        return md5(url.encode("utf8")).hexdigest()

    def fetch(self, force: bool = False) -> None:
        # TODO 记得修改shit code
        query = select(data.RemoteAssetCache).where(
            data.RemoteAssetCache.key == self.__key
        )
        with database.get_session().begin() as session:
            result = session.execute(query).scalar_one_or_none()
            need_fetch = (
                force
                or (result is None)
                or (
                    result.expire_time is not None
                    and result.expire_time < datetime.now()
                )
                or (result.expire_time is None and self.__expire is not None)
                or (not (self._cache_path / self.__key).exists())
            )

            if self.__expire is None:
                expire = None
            elif isinstance(self.__expire, timedelta):
                expire = datetime.now() + self.__expire
            else:
                expire = self.__expire

            if need_fetch:
                resp = _client.get(self.__url)
                if resp.is_success:
                    with (self._cache_path / self.__key).open("wb") as f:
                        f.write(resp.content)
                    self.__data = resp.content
                    if result is None:
                        session.execute(
                            insert(data.RemoteAssetCache).values(
                                key=self.__key,
                                fetch_time=datetime.now(),
                                expire_time=expire,
                            )
                        )
                    else:
                        session.execute(
                            update(data.RemoteAssetCache)
                            .where(data.RemoteAssetCache.key == self.__key)
                            .values(fetch_time=datetime.now(), expire_time=expire)
                        )
            else:
                self.__data = (self._cache_path / self.__key).read_bytes()

    def json(self) -> dict | list:
        self.fetch()
        if self.__data:
            return json.loads(self.__data.decode("utf-8"))
        return {}

    def text(self) -> str:
        self.fetch()
        if self.__data:
            return self.__data.decode("utf-8")
        return ""

    def raw(self) -> bytes | None:
        self.fetch()
        if self.__data:
            return self.__data
        return None


class LocalAsset(Asset):
    _asset_base_path = Path(__file__).parent.parent.parent / "assets"

    def __init__(self, path: str | Path):
        """
        :param path: 相对于assets文件夹的路径
        """
        self.__file_path: Path = self._asset_base_path / path
        self.__data = self.__file_path.read_bytes()

    def __getitem__(self, item):
        return self.json()[item]

    def __iter__(self):
        return iter(self.json())

    def fetch(self) -> None:
        self.__data = self.__file_path.read_bytes()

    def json(self) -> Any:
        return json.loads(self.text())

    def text(self) -> str:
        return self.__data.decode(encoding="utf-8")

    def raw(self) -> bytes:
        return self.__data

    def path(self) -> Path:
        return self.__file_path
