import json

from pytest_mock import MockerFixture


def test_read_json(mocker: MockerFixture):
    fake_data = {"key": "value"}
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(fake_data)))

    from essentials.libraries.file import read_json

    assert read_json("test.json") == fake_data
