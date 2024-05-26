from json import JSONDecodeError

import pytest
from httpx import Response
from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_fetch_json_data_fail(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=Response(
            status_code=200,
            content=b"<html><body>example</body></html>",
        ),
    )
    with pytest.raises(JSONDecodeError):
        assert await bilibili.fetch_json_data("https://example.com") is None


@pytest.mark.asyncio
async def test_fetch_video_data_bv(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "plugins.bilibili.bilibili.fetch_json_data",
        return_value={
            "code": 0,
            "data": {
                "bvid": "BV1PN4y187YT",
                "aid": 877501396,
            },
        },
    )

    data = await bilibili.fetch_video_data("BV1PN4y187YT")
    assert data
    assert data["bvid"] == "BV1PN4y187YT"


@pytest.mark.asyncio
async def test_fetch_video_data_av(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "plugins.bilibili.bilibili.fetch_json_data",
        return_value={
            "code": 0,
            "data": {
                "bvid": "BV1PN4y187YT",
                "aid": 877501396,
            },
        },
    )

    data = await bilibili.fetch_video_data("av877501396")
    assert data
    assert data["bvid"] == "BV1PN4y187YT"


@pytest.mark.asyncio
async def test_fetch_video_data_invalid_bv(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "plugins.bilibili.bilibili.fetch_json_data",
        return_value={"code": -400, "message": "请求错误", "ttl": 1},
    )

    data = await bilibili.fetch_video_data("BVinvalid-bv")
    assert data is None


@pytest.mark.asyncio
async def test_fetch_video_data_invalid_av(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "plugins.bilibili.bilibili.fetch_json_data",
        return_value={"code": -400, "message": "请求错误", "ttl": 1},
    )

    data = await bilibili.fetch_video_data("av0")
    assert data is None


@pytest.mark.asyncio
async def test_fetch_video_data_invalid_vid():
    from plugins.bilibili import bilibili

    data = await bilibili.fetch_video_data("invalid_vid")
    assert data is None


@pytest.mark.asyncio
async def test_get_bvid_from_short_link_valid(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=Response(
            status_code=302,
            headers={
                "location": "https://www.bilibili.com/video/BV1PN4y187YT",
            },
        ),
    )

    assert (
        await bilibili.get_bvid_from_short_link("https://b23.tv/clUJ8Xw")
        == "BV1PN4y187YT"
    )


@pytest.mark.asyncio
async def test_get_bvid_from_short_link_invalid(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=Response(
            status_code=200,
            content='{"code": -404,"message": "啥都木有","ttl": 1}'.encode("utf-8"),
        ),
    )

    assert await bilibili.get_bvid_from_short_link("https://b23.tv/invalid_url") is None


@pytest.mark.asyncio
async def test_fetch_all_projects(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "plugins.bilibili.bilibili.fetch_json_data",
        return_value={
            "errno": 0,
            "data": {
                "numPages": 1,
                "result": [
                    {
                        "id": 0,
                        "project_name": "example",
                    }
                ],
            },
        },
    )

    data = await bilibili.fetch_all_projects()
    assert data


@pytest.mark.asyncio
async def test_fetch_all_projects_invalid_area(mocker: MockerFixture):
    from plugins.bilibili import bilibili

    mocker.patch(
        "plugins.bilibili.bilibili.fetch_json_data",
        return_value={
            "errno": 0,
            "errtag": 0,
            "msg": "",
            "data": {
                "traceID": "",
                "total": 0,
                "numResults": 0,
                "numPages": 0,
                "page": 1,
                "pagesize": 0,
                "seid": "",
                "result": [],
            },
        },
    )

    data = await bilibili.fetch_all_projects("000000")
    assert data == []
