import pytest


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_fetch_json_data_fail():
    from plugins.bilibili import bilibili
    assert await bilibili.fetch_json_data("https://example.com") is None


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_fetch_video_data_bv():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_video_data("BV1PN4y187YT")
    assert data
    assert data["bvid"] == "BV1PN4y187YT"


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_fetch_video_data_av():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_video_data("av877501396")
    assert data
    assert data["bvid"] == "BV1PN4y187YT"


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_fetch_video_data_invalid_bv():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_video_data("BVinvalid-bv")
    assert data is None


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_fetch_video_data_invalid_av():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_video_data("av0")
    assert data is None


@pytest.mark.asyncio(scope="session")
async def test_fetch_video_data_invalid_vid():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_video_data("invalid_vid")
    assert data is None


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_get_bvid_from_short_link_valid():
    from plugins.bilibili import bilibili
    assert await bilibili.get_bvid_from_short_link("https://b23.tv/clUJ8Xw") == "BV1PN4y187YT"


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_get_bvid_from_short_link_invalid():
    from plugins.bilibili import bilibili
    assert await bilibili.get_bvid_from_short_link("https://b23.tv/invalid_url") is None


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_fetch_all_projects():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_all_projects()
    assert data


@pytest.mark.network
@pytest.mark.asyncio(scope="session")
async def test_fetch_all_projects_invalid_area():
    from plugins.bilibili import bilibili
    data = await bilibili.fetch_all_projects("000000")
    assert data == []
