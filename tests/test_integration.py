import os
import pytest

from ansys.grantami.recordlists import Connection
from ansys.grantami.recordlists.models import RecordList, RecordListItem


pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def sl_url():
    return os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")


@pytest.fixture(scope="session")
def list_admin_username():
    return os.getenv("TEST_LIST_ADMIN_USER")


@pytest.fixture(scope="session")
def list_admin_password():
    return os.getenv("TEST_LIST_ADMIN_PASS")


@pytest.fixture(scope="session")
def api_client(sl_url, list_admin_username, list_admin_password):
    connection = Connection(f"{sl_url}/proxy/v1.svc").with_credentials(
        list_admin_username, list_admin_password
    )
    return connection.connect()


TEST_LIST_NAME = "IntegrationTestList"


@pytest.fixture
def new_list_id(api_client):
    list_id = api_client._create_list(name=TEST_LIST_NAME)
    yield list_id
    # TODO delete


@pytest.fixture
def new_list_with_items(api_client, new_list_id):
    record_list = api_client.get_list(new_list_id)
    items = [
        RecordListItem(
            "e595fe23-b450-4d18-8c08-4a0f378ef095",
            "81dff531-0254-4fbe-9621-174b10aaee3d",
            "3bc2b82f-0199-4f3b-a7af-8d520250b180",
        )
    ]
    record_list.add_items(items)
    return new_list_id


def test_getting_all_lists(api_client, new_list_id):
    # Using new_list_id fixture to ensure there is at least one list when this test is run
    all_lists = api_client.get_all_lists()
    assert isinstance(all_lists, list)
    assert all(isinstance(l, RecordList) for l in all_lists)


def test_get_list_and_items(api_client, new_list_with_items):
    record_list = api_client.get_list(new_list_with_items)

    assert record_list._items is None
    assert isinstance(record_list.items, list)
    assert all(isinstance(item, RecordListItem) for item in record_list.items)


def test_create_minimal_list(api_client):
    name = "IntegrationTestList"
    record_list = api_client.create_list(name=name)

    assert record_list.name == name
    assert isinstance(record_list.identifier, str)


def test_create_list_from_class(api_client):
    my_list = RecordList(
        api_client,
        name="IntegrationTestList",
    )
    with pytest.raises(RuntimeError):
        list_id = my_list.identifier

    my_list.create()
    assert my_list.identifier is not None
