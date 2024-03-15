import pytest


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_short_link():
    from plugins.bilibili import bilibili
    assert await bilibili.get_bvid_from_short_link("https://b23.tv/clUJ8Xw") == "BV1PN4y187YT"


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_get_video_data_by_bv():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_video_data("BV1PN4y187YT")
    assert data
    assert data["bvid"] == "BV1PN4y187YT"


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_get_video_data_by_av():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_video_data("av877501396")
    assert data
    assert data["bvid"] == "BV1PN4y187YT"


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_get_projects():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_all_projects()
    assert data
