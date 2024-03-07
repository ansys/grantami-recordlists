import os
import uuid

from ansys.grantami.serverapi_openapi.api import SchemaDatabasesApi, SearchApi
from ansys.grantami.serverapi_openapi.models import (
    GrantaServerApiSearchDiscreteTextValuesDatumCriterion,
    GrantaServerApiSearchRecordPropertyCriterion,
    GrantaServerApiSearchSearchableRecordProperty,
    GrantaServerApiSearchSearchRequest,
)
import pytest

from ansys.grantami.recordlists import Connection, RecordListItem

DB_KEY = "MI_Training"


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
            client.delete_list(record_list)


@pytest.fixture(scope="session")
def basic_client(sl_url, list_username_no_permissions, list_password_no_permissions, list_name):
    """
    Fixture providing a real ApiClient to run integration tests against an instance of Granta MI
    Server API.
    On teardown, deletes all lists named using the fixture `list_name`.
    """
    connection = Connection(sl_url).with_credentials(
        list_username_no_permissions,
        list_password_no_permissions,
    )
    client = connection.connect()
    yield client

    all_lists = client.get_all_lists()
    for record_list in all_lists:
        if list_name in record_list.name:
            client.delete_list(record_list)


@pytest.fixture(scope="session")
def unique_id():
    """Generate a unique id for the test session. Used to keep track of record lists created
    during the session"""
    return uuid.uuid4()


@pytest.fixture(scope="session")
def list_name(unique_id):
    """
    Provides a name for new lists. All lists created with this name are deleted on teardown of
    `api_client`.
    """
    prefix = "IntegrationTestList"
    return f"{prefix}_{unique_id}"


@pytest.fixture
def new_list(admin_client, request, list_name):
    """
    Provides the identifier of newly created list.
    The created list include the name of the calling test as a `description`.
    """
    new_list = admin_client.create_list(name=list_name, description=request.node.name)
    cleanup = getattr(request, "param", {}).get("cleanup", True)
    yield new_list
    if cleanup:
        admin_client.delete_list(new_list)


@pytest.fixture
def new_list_with_one_unresolvable_item(admin_client, new_list, unresolvable_item):
    items = [unresolvable_item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_list_with_many_unresolvable_items(admin_client, new_list, many_unresolvable_items):
    admin_client.add_items_to_list(new_list, many_unresolvable_items)
    return new_list


@pytest.fixture(scope="session")
def db_key_to_guid_map(admin_client):
    schema_api = SchemaDatabasesApi(admin_client)
    dbs = schema_api.get_all_databases()
    return {db.key: db.guid for db in dbs.databases}


@pytest.fixture(scope="session")
def resolvable_records(admin_client):
    """Get all records in the MI_Training database"""
    search_api = SearchApi(admin_client)
    search_body = GrantaServerApiSearchSearchRequest(
        criterion=GrantaServerApiSearchRecordPropertyCriterion(
            _property=GrantaServerApiSearchSearchableRecordProperty.RECORDTYPE,
            inner_criterion=GrantaServerApiSearchDiscreteTextValuesDatumCriterion(
                any=["Record", "Generic", "Folder"],
            ),
        )
    )
    search_results = search_api.database_search(
        database_key=DB_KEY,
        body=search_body,
    )
    return search_results.results


@pytest.fixture(scope="session")
def resolvable_item(resolvable_records, db_key_to_guid_map):
    first_result = resolvable_records[0]
    return RecordListItem(
        db_key_to_guid_map[first_result.database_key],
        first_result.table_guid,
        first_result.record_history_guid,
    )


@pytest.fixture
def new_list_with_one_resolvable_item(admin_client, new_list, resolvable_item):
    items = [resolvable_item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture(scope="session")
def many_resolvable_items(resolvable_records, db_key_to_guid_map):
    results = resolvable_records
    items = [
        RecordListItem(
            db_key_to_guid_map[result.database_key],
            result.table_guid,
            result.record_history_guid,
        )
        for result in results
    ]
    return items


@pytest.fixture
def new_list_with_many_resolvable_items(admin_client, new_list, many_resolvable_items):
    admin_client.add_items_to_list(new_list, many_resolvable_items)
    return new_list


@pytest.fixture
def new_list_with_many_resolvable_and_unresolvable_items(
    admin_client, new_list, many_resolvable_items, many_unresolvable_items
):
    admin_client.add_items_to_list(new_list, many_resolvable_items + many_unresolvable_items)
    return new_list


@pytest.fixture(scope="function")
def cleanup_admin(admin_client):
    to_delete = []
    yield to_delete
    for record_list in to_delete:
        admin_client.delete_list(record_list)


@pytest.fixture(scope="function")
def cleanup_basic(basic_client):
    to_delete = []
    yield to_delete
    for record_list in to_delete:
        basic_client.delete_list(record_list)
