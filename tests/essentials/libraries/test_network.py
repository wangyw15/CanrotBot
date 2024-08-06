import importlib

import pytest
from pytest_mock import MockerFixture


def test_create_client_without_proxy(mocker: MockerFixture):
    config = mocker.stub("NetworkConfig")
    config.user_data_path = "./canrot_data"
    config.proxy = ""

    mocker.patch(
        "nonebot.get_plugin_config",
        return_value=config
    )

    fake_client = mocker.stub("httpx.AsyncClient")
    mocker.patch(
        "httpx.AsyncClient",
        new=fake_client
    )

    import essentials.libraries.network

    assert essentials.libraries.network.network_config.proxy == config.proxy
    assert essentials.libraries.network.client
    fake_client.assert_called_once_with()


@pytest.mark.skip("Unable to test with proxy")
def test_create_client_with_proxy(mocker: MockerFixture):
    config = mocker.stub("NetworkConfig")
    config.user_data_path = "./canrot_data"
    config.proxy = "http://localhost:7890"

    mocker.patch(
        "nonebot.get_plugin_config",
        return_value=config
    )

    fake_client = mocker.stub("httpx.AsyncClient")
    mocker.patch(
        "httpx.AsyncClient",
        new=fake_client
    )

    import essentials.libraries.network
    importlib.reload(essentials.libraries.network)

    assert essentials.libraries.network.network_config.proxy == config.proxy
    assert essentials.libraries.network.client
    fake_client.assert_called_once_with(proxy=config.proxy)


@pytest.mark.asyncio
async def test_fetch_bytes_data(mocker: MockerFixture):
    from essentials.libraries.network import fetch_bytes_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 200
    resp.content = b"test"

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_bytes_data("https://example.com", use_proxy=False) == b"test"


@pytest.mark.asyncio
async def test_fetch_bytes_data_with_success_false(mocker: MockerFixture):
    from essentials.libraries.network import fetch_bytes_data

    resp = mocker.Mock()
    resp.is_success = False

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_bytes_data("https://example.com", use_proxy=False) is None


@pytest.mark.asyncio
async def test_fetch_bytes_data_with_status_code_not_200(mocker: MockerFixture):
    from essentials.libraries.network import fetch_bytes_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 404

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_bytes_data("https://example.com", use_proxy=False) is None


@pytest.mark.asyncio
async def test_fetch_json_data(mocker: MockerFixture):
    from essentials.libraries.network import fetch_json_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 200
    resp.json.return_value = {"test": "test"}

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_json_data("https://example.com", use_proxy=False) == {"test": "test"}


@pytest.mark.asyncio
async def test_fetch_json_data_with_success_false(mocker: MockerFixture):
    from essentials.libraries.network import fetch_json_data

    resp = mocker.Mock()
    resp.is_success = False

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_json_data("https://example.com", use_proxy=False) is None


@pytest.mark.asyncio
async def test_fetch_json_data_with_status_code_not_200(mocker: MockerFixture):
    from essentials.libraries.network import fetch_json_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 404

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_json_data("https://example.com", use_proxy=False) is None


@pytest.mark.asyncio
async def test_fetch_text_data(mocker: MockerFixture):
    from essentials.libraries.network import fetch_text_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 200
    resp.text = "test"

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_text_data("https://example.com", use_proxy=False) == "test"


@pytest.mark.asyncio
async def test_fetch_text_data_with_success_false(mocker: MockerFixture):
    from essentials.libraries.network import fetch_text_data

    resp = mocker.Mock()
    resp.is_success = False

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_text_data("https://example.com", use_proxy=False) is None


@pytest.mark.asyncio
async def test_fetch_text_data_with_status_code_not_200(mocker: MockerFixture):
    from essentials.libraries.network import fetch_text_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 404

    stub_get = mocker.async_stub("AsyncClient.get")
    stub_get.return_value = resp

    mocker.patch(
        "essentials.libraries.network.client.get",
        new=stub_get
    )

    assert await fetch_text_data("https://example.com", use_proxy=False) is None
