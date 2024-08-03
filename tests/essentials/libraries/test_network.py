import pytest
from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_create_client(mocker: MockerFixture):
    # from essentials.libraries.network.config import NetworkConfig
    #
    # config = NetworkConfig()
    # config.proxy = ""
    #
    # mocker.patch(
    #     "essentials.libraries.network.get_plugin_config",
    #     return_value=config
    # )

    initializer = mocker.stub("AsyncClient.__new__")
    mocker.patch(
        "essentials.libraries.network.AsyncClient.__new__",
        new_callable=initializer
    )

    import essentials.libraries.network

    assert essentials.libraries.network.client
    initializer.assert_called_once_with()


@pytest.mark.asyncio
async def test_fetch_bytes_data(mocker: MockerFixture):
    from essentials.libraries.network import fetch_bytes_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 200
    resp.content = b"test"

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_bytes_data("http://test.com") == b"test"


@pytest.mark.asyncio
async def test_fetch_bytes_data_with_success_false(mocker: MockerFixture):
    from essentials.libraries.network import fetch_bytes_data

    resp = mocker.Mock()
    resp.is_success = False

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_bytes_data("http://test.com") is None


@pytest.mark.asyncio
async def test_fetch_bytes_data_with_status_code_not_200(mocker: MockerFixture):
    from essentials.libraries.network import fetch_bytes_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 404

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_bytes_data("http://test.com") is None


@pytest.mark.asyncio
async def test_fetch_json_data(mocker: MockerFixture):
    from essentials.libraries.network import fetch_json_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 200
    resp.json.return_value = {"test": "test"}

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_json_data("http://test.com") == {"test": "test"}


@pytest.mark.asyncio
async def test_fetch_json_data_with_success_false(mocker: MockerFixture):
    from essentials.libraries.network import fetch_json_data

    resp = mocker.Mock()
    resp.is_success = False

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_json_data("http://test.com") is None


@pytest.mark.asyncio
async def test_fetch_json_data_with_status_code_not_200(mocker: MockerFixture):
    from essentials.libraries.network import fetch_json_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 404

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_json_data("http://test.com") is None


@pytest.mark.asyncio
async def test_fetch_text_data(mocker: MockerFixture):
    from essentials.libraries.network import fetch_text_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 200
    resp.text = "test"

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_text_data("http://test.com") == "test"


@pytest.mark.asyncio
async def test_fetch_text_data_with_success_false(mocker: MockerFixture):
    from essentials.libraries.network import fetch_text_data

    resp = mocker.Mock()
    resp.is_success = False

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_text_data("http://test.com") is None


@pytest.mark.asyncio
async def test_fetch_text_data_with_status_code_not_200(mocker: MockerFixture):
    from essentials.libraries.network import fetch_text_data

    resp = mocker.Mock()
    resp.is_success = True
    resp.status_code = 404

    mocker.patch(
        "essentials.libraries.network.client.get",
        return_value=resp
    )

    assert await fetch_text_data("http://test.com") is None
