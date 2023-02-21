import os
import uuid

import pytest

from ansys.openapi.common import ApiException
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
def api_client(sl_url, list_admin_username, list_admin_password, list_name):
    """
    Fixture providing a real ApiClient to run integration tests against an instance of Granta MI
    Server API.
    On teardown, deletes all lists named using the fixture `list_name`.
    """
    connection = Connection(sl_url).with_credentials(list_admin_username, list_admin_password)
    client = connection.connect()
    yield client

    all_lists = client.get_all_lists()
    for record_list in all_lists:
        if record_list.name == list_name:
            client.delete_list(record_list.identifier)


@pytest.fixture(scope="session")
def list_name():
    """
    Provides a name for new lists. All lists created with this name are deleted on teardown of
    `api_client`.
    """
    prefix = "IntegrationTestList"
    _uuid = uuid.uuid4()
    return f"{prefix}_{_uuid}"


@pytest.fixture
def new_list_id(api_client, request, list_name):
    """
    Provides the identifier of newly created list.
    The created list include the name of the calling test as a `description`.
    """
    list_id = api_client._create_list(name=list_name, description=request.node.name)
    cleanup = getattr(request, "param", {}).get("cleanup", True)
    yield list_id
    if cleanup:
        api_client.delete_list(list_id)


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
    my_list = next(rl for rl in all_lists if rl.identifier == new_list_id)


def test_get_list_and_items(api_client, new_list_with_items):
    record_list = api_client.get_list(new_list_with_items)

    assert record_list._items is None
    assert isinstance(record_list.items, list)
    assert all(isinstance(item, RecordListItem) for item in record_list.items)


def test_create_minimal_list(api_client, list_name):
    record_list = api_client.create_list(name=list_name)

    assert record_list.name == list_name
    assert isinstance(record_list.identifier, str)


def test_create_list_from_class(api_client, list_name):
    my_list = RecordList(
        api_client,
        name=list_name,
    )
    with pytest.raises(RuntimeError):
        list_id = my_list.identifier

    my_list.create()
    assert my_list.identifier is not None


@pytest.mark.parametrize("new_list_id", [{"cleanup": False}], indirect=True)
def test_delete_list(api_client, new_list_id, list_name):
    api_client.delete_list(new_list_id)

    with pytest.raises(ApiException) as exc:
        my_list = api_client.get_list(new_list_id)
    assert exc.value.status_code == 404


def test_update_list(api_client, new_list_id):
    api_client.update_list(new_list_id, name="NEWUPDATEDNAME")
    record_list = api_client.get_list(new_list_id)
    assert record_list.name == "NEWUPDATEDNAME"


def test_update_list_nullable_property(api_client, new_list_id):
    api_client.update_list(new_list_id, notes="Some notes")
    record_list = api_client.get_list(new_list_id)
    assert record_list.notes == "Some notes"

    api_client.update_list(new_list_id, notes=None)
    record_list = api_client.get_list(new_list_id)
    assert record_list.notes is None
