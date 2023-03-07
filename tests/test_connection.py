import re

import pytest

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
