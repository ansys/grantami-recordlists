# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

from requests_mock import ANY


def test_get_all_lists(mock_client, mocker, mock_response):
    with mocker:
        mocker.get(ANY, status_code=200, json=mock_response)
        response = mock_client.get_all_lists()

    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].name == "Test List"
    assert response[1].name == "CreateTest"


def test_get_single_list(mock_client, mocker, mock_response):
    with mocker:
        mocker.get(ANY, status_code=200, json=mock_response)
        response = mock_client.get_list("bffba6ef-b85a-4b26-932b-00875b74ca2e")

    assert response.name == "Test List"
