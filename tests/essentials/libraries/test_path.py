from pathlib import Path


def test_get_asset_path():
    from canrotbot.essentials.libraries import path

    assert path.get_asset_path().resolve() == (Path(__file__).parent.parent.parent.parent / "assets").resolve()
    assert path.get_asset_path("test").resolve() == (Path(__file__).parent.parent.parent.parent / "assets" / "test").resolve()


def test_get_cache_path():
    from canrotbot.essentials.libraries import path

    assert path.get_cache_path().resolve() == (Path(path.config.user_data_path) / "cache").resolve()
    assert path.get_cache_path("test").resolve() == (Path(path.config.user_data_path) / "cache" / "test").resolve()


def test_get_data_path():
    from canrotbot.essentials.libraries import path

    assert path.get_data_path("test").resolve() == (Path(path.config.user_data_path) / "data" / "test").resolve()
