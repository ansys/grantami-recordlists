# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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


def test_new_server_version(sl_url, successful_auth, mocker):
    mi_version_response = {
        "binary_compatibility_version": "25.2.0.0",
        "version": "25.2.820.0",
        "major_minor_version": "25.2",
    }

    with mocker:
        connection = Connection(sl_url).with_anonymous()
        mocker.get(requests_mock.ANY, status_code=200, json=mi_version_response)
        connection.connect()


def test_old_server_version_is_handled(sl_url, successful_auth, mocker):
    mi_version_response = {
        "binary_compatibility_version": "12.0.0.0",
        "version": "12.1.2.3",
        "major_minor_version": "12.0",
    }

    with mocker:
        connection = Connection(sl_url).with_anonymous()
        mocker.get(requests_mock.ANY, status_code=200, json=mi_version_response)
        with pytest.raises(
            ConnectionError,
            match=r"This package requires a more recent Granta MI version.*12\.1.*24\.2",
        ):
            connection.connect()


def test_server_version_error_is_handled(sl_url, successful_auth, mocker):
    with mocker:
        connection = Connection(sl_url).with_anonymous()
        mocker.get(requests_mock.ANY, status_code=200, json={})
        version_path = re.compile("schema/mi-version")
        mocker.get(version_path, status_code=404)
        with pytest.raises(
            ConnectionError,
            match=r"Cannot find the Server API definition in Granta MI Service Layer",
        ):
            connection.connect()
