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

import json
import uuid

import pytest
import requests_mock

from ansys.grantami.recordlists import Connection, RecordListItem
from inputs.examples import examples_as_strings

MI_VERSION_RESPONSE = {
    "binary_compatibility_version": "99.99.0.0",
    "version": "99.99.9.9",
    "major_minor_version": "99.99",
}


@pytest.fixture(scope="session")
def api_url():
    return "http://localhost/mi_servicelayer"


@pytest.fixture()
def mocker():
    m = requests_mock.Mocker()
    return m


@pytest.fixture
def mock_client(api_url, mocker):
    with mocker:
        mocker.get(requests_mock.ANY, status_code=200, json=MI_VERSION_RESPONSE)
        client = Connection(servicelayer_url=api_url).with_anonymous().connect()
    return client


@pytest.fixture
def mock_response(request):
    response_text = examples_as_strings.get(request.node.name)
    return json.loads(response_text)


@pytest.fixture(scope="session")
def unresolvable_item():
    # GUIDs need only have the correct format for record lists test to pass.
    return RecordListItem(
        "e595fe23-b450-4d18-8c08-4a0f378ef095",
        "81dff531-0254-4fbe-9621-174b10aaee3d",
        "3bc2b82f-0199-4f3b-a7af-8d520250b180",
    )


@pytest.fixture(scope="session")
def many_unresolvable_items():
    # GUIDs need only have the correct format for record lists test to pass.
    results = []
    for i in range(5000):
        results.append(
            RecordListItem(
                database_guid="e595fe23-b450-4d18-8c08-4a0f378ef095",
                table_guid=str(uuid.uuid4()),
                record_history_guid=str(uuid.uuid4()),
            )
        )
    return results
