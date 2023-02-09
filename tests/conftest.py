import json
import pytest
import requests_mock

from ansys.grantami.recordlists import ServerApiFactory

from inputs.examples import examples_as_strings


@pytest.fixture(scope="session")
def api_url():
    return "http://localhost/mi_servicelayer/proxy/v1.svc"


@pytest.fixture()
def mocker():
    m = requests_mock.Mocker()
    return m


@pytest.fixture
def mock_client(api_url, mocker):
    with mocker:
        mocker.get(requests_mock.ANY)
        client = ServerApiFactory(api_url=api_url).with_anonymous().connect()
    return client


@pytest.fixture
def mock_response(request):
    response_text = examples_as_strings.get(request.node.name)
    return json.loads(response_text)
