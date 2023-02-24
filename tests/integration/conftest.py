import os
import uuid

import pytest

from ansys.grantami.recordlists import Connection
from ansys.grantami.recordlists.models import RecordListItem


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
def list_username_no_permissions():
    return os.getenv("TEST_LIST_USER")


@pytest.fixture(scope="session")
def list_password_no_permissions():
    return os.getenv("TEST_LIST_PASS")


@pytest.fixture(scope="session")
def admin_client(sl_url, list_admin_username, list_admin_password, list_name):
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
        if list_name in record_list.name:
            client.delete_list(record_list.identifier)


@pytest.fixture(scope="session")
def basic_client(sl_url, list_username_no_permissions, list_password_no_permissions, list_name):
    """
    Fixture providing a real ApiClient to run integration tests against an instance of Granta MI
    Server API.

    """
    connection = Connection(sl_url).with_credentials(
        list_username_no_permissions, list_password_no_permissions
    )
    client = connection.connect()
    yield client

    all_lists = client.get_all_lists()
    for record_list in all_lists:
        if list_name in record_list.name:
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
def new_list_id(admin_client, request, list_name):
    """
    Provides the identifier of newly created list.
    The created list include the name of the calling test as a `description`.
    """
    list_id = admin_client.create_list(name=list_name, description=request.node.name)
    cleanup = getattr(request, "param", {}).get("cleanup", True)
    yield list_id
    if cleanup:
        admin_client.delete_list(list_id)


@pytest.fixture
def new_list_with_items(admin_client, new_list_id):
    items = [
        RecordListItem(
            "e595fe23-b450-4d18-8c08-4a0f378ef095",
            "81dff531-0254-4fbe-9621-174b10aaee3d",
            "3bc2b82f-0199-4f3b-a7af-8d520250b180",
        )
    ]
    admin_client.add_items_to_list(new_list_id, items)
    return new_list_id
