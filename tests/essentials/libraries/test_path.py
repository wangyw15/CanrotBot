from pathlib import Path


def test_get_asset_path():
    from essentials.libraries import path

    assert path.get_asset_path() == Path(__file__).parent.parent.parent.parent / "assets"
    assert path.get_asset_path("test") == Path(__file__).parent.parent.parent.parent / "assets" / "test"


def test_get_cache_path():
    from essentials.libraries import path

    assert path.get_cache_path() == Path(path.config.user_data_path) / "cache"
    assert path.get_cache_path("test") == Path(path.config.user_data_path) / "cache" / "test"


def test_get_data_path():
    from essentials.libraries import path

    assert path.get_data_path("test") == Path(path.config.user_data_path) / "data" / "test"
