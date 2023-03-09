import re

import pytest
import requests.exceptions
import requests_mock

from ansys.grantami.recordlists import Connection
from ansys.grantami.recordlists._connection import AUTH_PATH, PROXY_PATH


@pytest.fixture
def sl_url():
    return "http://host/path"


@pytest.fixture
def successful_auth(mocker, sl_url):
    with mocker:
        mocker.get(sl_url)
        mocker.get(sl_url + AUTH_PATH)


def test_missing_api_definition_raises_informative_error(sl_url, successful_auth, mocker):
    with mocker:
        service_matcher = re.compile(f"{sl_url}{PROXY_PATH}.*")
        mocker.get(service_matcher, status_code=404)
        with pytest.raises(
            ConnectionError,
            match="Cannot find the Server API definition in Granta MI Service Layer",
        ):
            Connection(sl_url).with_anonymous().connect()


def test_unhandled_test_connection_response_raises_informative_error(
    sl_url, successful_auth, mocker
):
    with mocker:
        service_matcher = re.compile(f"{sl_url}{PROXY_PATH}.*")
        mocker.get(service_matcher, status_code=500)
        with pytest.raises(ConnectionError, match="An unexpected error occurred"):
            Connection(sl_url).with_anonymous().connect()


def test_500_on_test_connection_is_handled(sl_url, successful_auth, mocker):
    with mocker:
        connection = Connection(sl_url).with_anonymous()
        mocker.get(requests_mock.ANY, exc=requests.exceptions.RetryError)
        with pytest.raises(
            ConnectionError, match="Check that SSL certificates have been configured"
        ):
            client = connection.connect()
