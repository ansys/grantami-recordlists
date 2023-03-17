import json

import pytest
import requests_mock

from ansys.grantami.recordlists import Connection, RecordListItem
from inputs.examples import examples_as_strings


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
        mocker.get(requests_mock.ANY)
        client = Connection(servicelayer_url=api_url).with_anonymous().connect()
    return client


@pytest.fixture
def mock_response(request):
    response_text = examples_as_strings.get(request.node.name)
    return json.loads(response_text)


@pytest.fixture(scope="session")
def example_item():
    # GUIDs need only have the correct format for record lists test to pass.
    return RecordListItem(
        "e595fe23-b450-4d18-8c08-4a0f378ef095",
        "81dff531-0254-4fbe-9621-174b10aaee3d",
        "3bc2b82f-0199-4f3b-a7af-8d520250b180",
    )
