import os
from typing import Dict, List
import uuid

from ansys.grantami.serverapi_openapi.api import SchemaDatabasesApi, SchemaTablesApi, SearchApi
from ansys.grantami.serverapi_openapi.models import (
    GrantaServerApiSearchDiscreteTextValuesDatumCriterion,
    GrantaServerApiSearchRecordPropertyCriterion,
    GrantaServerApiSearchSearchableRecordProperty,
    GrantaServerApiSearchSearchRequest,
    GrantaServerApiVersionState,
)
from common import (
    DB_KEY,
    TABLE_NAME,
    create_new_unreleased_version,
    ensure_history_exists,
    get_latest_version_info,
    get_version_info_in_state,
    release_version,
    supersede_version,
)
import pytest

from ansys.grantami.recordlists import Connection, RecordList, RecordListItem, RecordListsApiClient


@pytest.fixture(scope="session")
def sl_url() -> str:
    return os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")


@pytest.fixture(scope="session")
def list_admin_username() -> str:
    return os.getenv("TEST_LIST_ADMIN_USER")


@pytest.fixture(scope="session")
def list_admin_password() -> str:
    return os.getenv("TEST_LIST_ADMIN_PASS")


@pytest.fixture(scope="session")
def list_username_no_permissions() -> str:
    return os.getenv("TEST_LIST_USER")


@pytest.fixture(scope="session")
def list_password_no_permissions() -> str:
    return os.getenv("TEST_LIST_PASS")


@pytest.fixture(scope="session")
def admin_client(
    sl_url, list_admin_username, list_admin_password, list_name
) -> RecordListsApiClient:
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
def basic_client(
    sl_url, list_username_no_permissions, list_password_no_permissions, list_name
) -> RecordListsApiClient:
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
def unique_id() -> uuid.UUID:
    """Generate a unique id for the test session. Used to keep track of record lists created
    during the session"""
    return uuid.uuid4()


@pytest.fixture(scope="session")
def list_name(unique_id) -> str:
    """
    Provides a name for new lists. All lists created with this name are deleted on teardown of
    `api_client`.
    """
    prefix = "IntegrationTestList"
    return f"{prefix}_{unique_id}"


@pytest.fixture
def new_list(admin_client, request, list_name) -> RecordList:
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
def new_list_with_one_unresolvable_item(admin_client, new_list, unresolvable_item) -> RecordList:
    items = [unresolvable_item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_list_with_many_unresolvable_items(
    admin_client, new_list, many_unresolvable_items
) -> RecordList:
    admin_client.add_items_to_list(new_list, many_unresolvable_items)
    return new_list


@pytest.fixture(scope="session")
def db_key_to_guid_map(admin_client) -> Dict[str, str]:
    schema_api = SchemaDatabasesApi(admin_client)
    dbs = schema_api.get_all_databases()
    return {db.key: db.guid for db in dbs.databases}


@pytest.fixture(scope="session")
def resolvable_items(admin_client, db_key_to_guid_map) -> List[RecordListItem]:
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
    return [
        RecordListItem(
            db_key_to_guid_map[result.database_key],
            result.table_guid,
            result.record_history_guid,
        )
        for result in search_results.results
    ]


@pytest.fixture
def new_list_with_one_resolvable_item(admin_client, new_list, resolvable_items) -> RecordList:
    admin_client.add_items_to_list(new_list, [resolvable_items[0]])
    return new_list


@pytest.fixture
def new_list_with_many_resolvable_items(admin_client, new_list, resolvable_items) -> RecordList:
    admin_client.add_items_to_list(new_list, resolvable_items)
    return new_list


@pytest.fixture
def new_list_with_many_resolvable_and_unresolvable_items(
    admin_client, new_list, resolvable_items, many_unresolvable_items
) -> RecordList:
    admin_client.add_items_to_list(new_list, resolvable_items + many_unresolvable_items)
    return new_list


@pytest.fixture(scope="session")
def table_guid(admin_client) -> str:
    tables_api = SchemaTablesApi(admin_client)
    all_tables = tables_api.get_tables(
        database_key=DB_KEY,
    )
    assert all_tables is not None
    table_guid = next(table.guid for table in all_tables.tables if table.name == TABLE_NAME)
    return table_guid


@pytest.fixture(scope="session")
def unreleased_item(admin_client, table_guid, db_key_to_guid_map) -> RecordListItem:
    history_guid = ensure_history_exists(admin_client, table_guid, "UnreleasedRecord")
    version_state, _, version_number = get_latest_version_info(admin_client, history_guid)
    if version_state != GrantaServerApiVersionState.UNRELEASED:
        # This record must contain a single unreleased version only. If the latest version
        # is not unreleased, raise a RuntimeError
        raise RuntimeError(f"Unexpected record version state {version_state}.")
    return RecordListItem(db_key_to_guid_map[DB_KEY], table_guid, history_guid, version_number)


@pytest.fixture(scope="session")
def released_item(admin_client, table_guid, db_key_to_guid_map) -> RecordListItem:
    history_guid = ensure_history_exists(admin_client, table_guid, "ReleasedRecord")
    version_state, version_guid, version_number = get_latest_version_info(
        admin_client, history_guid
    )
    if version_state == GrantaServerApiVersionState.UNRELEASED:
        # If the record is unreleased, release it.
        release_version(admin_client, table_guid, history_guid, version_guid)
    elif version_state == GrantaServerApiVersionState.RELEASED:
        # If the record is already released, do nothing
        pass
    elif version_state in [
        GrantaServerApiVersionState.SUPERSEDED,
        GrantaServerApiVersionState.UNVERSIONED,
        GrantaServerApiVersionState.WITHDRAWN,
    ]:
        # Either the record is in an unversioned table, or has already been superseded or withdrawn. Raise exception.
        raise RuntimeError(f"Unexpected record version state {version_state}.")
    return RecordListItem(db_key_to_guid_map[DB_KEY], table_guid, history_guid, version_number)


@pytest.fixture(scope="session")
def superseded_item(admin_client, table_guid, db_key_to_guid_map) -> RecordListItem:
    history_guid = ensure_history_exists(admin_client, table_guid, "SupersededRecord")
    try:
        version_state, version_guid, version_number = get_version_info_in_state(
            admin_client, history_guid, GrantaServerApiVersionState.SUPERSEDED
        )
        # We have a superseded record as required
    except ValueError:
        version_state, version_guid, version_number = get_latest_version_info(
            admin_client, history_guid
        )
        if version_state == GrantaServerApiVersionState.UNRELEASED and version_number == 2:
            # If v2 is unreleased, release it, which will supersede v1.
            release_version(admin_client, table_guid, history_guid, version_guid)
            # Re-fetch the information for the newly-superseded record
            version_state, version_guid, version_number = get_version_info_in_state(
                admin_client, history_guid, GrantaServerApiVersionState.SUPERSEDED
            )
        elif version_state == GrantaServerApiVersionState.UNRELEASED and version_number == 1:
            # If v1 is unreleased, we need to release it and then supersede it
            release_version(admin_client, table_guid, history_guid, version_guid)
            supersede_version(admin_client, table_guid, history_guid, version_guid)
        elif version_state in [
            GrantaServerApiVersionState.RELEASED,
            GrantaServerApiVersionState.WITHDRAWN,
        ]:
            # If v1 is released or withdrawn, just supersede it
            supersede_version(admin_client, table_guid, history_guid, version_guid)
        elif version_state == GrantaServerApiVersionState.UNVERSIONED:
            # Unversioned table
            raise RuntimeError(f"Unexpected record version state {version_state}.")
    return RecordListItem(db_key_to_guid_map[DB_KEY], table_guid, history_guid, version_number)


@pytest.fixture(scope="session")
def draft_superseded_item(admin_client, table_guid, db_key_to_guid_map) -> RecordListItem:
    history_guid = ensure_history_exists(admin_client, table_guid, "DraftSupersededRecord")
    try:
        version_state, version_guid, version_number = get_version_info_in_state(
            admin_client, history_guid, GrantaServerApiVersionState.UNRELEASED, version_number=2
        )
        # We have a v2 unreleased record (and a v1 released record)
        return RecordListItem(
            db_key_to_guid_map[DB_KEY],
            table_guid,
            history_guid,
            version_number,
        )
    except ValueError:
        version_state, version_guid, version_number = get_latest_version_info(
            admin_client, history_guid
        )
        if version_state == GrantaServerApiVersionState.UNRELEASED:
            # v1 unreleased only. Release v1 and then create a new unreleased v2
            release_version(admin_client, table_guid, history_guid, version_guid)
            create_new_unreleased_version(admin_client, table_guid, history_guid, version_guid)
        elif version_state in [
            GrantaServerApiVersionState.RELEASED,
            GrantaServerApiVersionState.WITHDRAWN,
        ]:
            # v1 is released or withdrawn. Create a new unreleased v2
            create_new_unreleased_version(admin_client, table_guid, history_guid, version_guid)
        elif version_state == GrantaServerApiVersionState.UNVERSIONED:
            # Unversioned table
            raise RuntimeError(f"Unexpected record version state {version_state}.")

    # Fetch the information for the unreleased v2 record
    version_state, version_guid, version_number = get_version_info_in_state(
        admin_client, history_guid, GrantaServerApiVersionState.UNRELEASED, version_number=2
    )
    return RecordListItem(db_key_to_guid_map[DB_KEY], table_guid, history_guid, version_number)


@pytest.fixture
def new_admin_list_with_one_unreleased_item(admin_client, new_list, unreleased_item) -> RecordList:
    items = [unreleased_item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_admin_list_with_one_unreleased_item_by_history(
    admin_client, new_list, unreleased_item
) -> RecordList:
    item = RecordListItem(
        database_guid=unreleased_item.database_guid,
        table_guid=unreleased_item.table_guid,
        record_history_guid=unreleased_item.record_history_guid,
    )
    items = [item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_admin_list_with_one_released_item(admin_client, new_list, released_item) -> RecordList:
    items = [released_item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_admin_list_with_one_released_item_by_history(
    admin_client, new_list, released_item
) -> RecordList:
    item = RecordListItem(
        database_guid=released_item.database_guid,
        table_guid=released_item.table_guid,
        record_history_guid=released_item.record_history_guid,
    )
    items = [item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_admin_list_with_one_superseded_item(admin_client, new_list, superseded_item) -> RecordList:
    items = [superseded_item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_admin_list_with_one_superseded_item_by_history(
    admin_client, new_list, superseded_item
) -> RecordList:
    item = RecordListItem(
        database_guid=superseded_item.database_guid,
        table_guid=superseded_item.table_guid,
        record_history_guid=superseded_item.record_history_guid,
    )
    items = [item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_admin_list_with_one_draft_superseded_item(
    admin_client, new_list, draft_superseded_item
) -> RecordList:
    items = [draft_superseded_item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_admin_list_with_one_draft_superseded_item_by_history(
    admin_client, new_list, draft_superseded_item
) -> RecordList:
    item = RecordListItem(
        database_guid=draft_superseded_item.database_guid,
        table_guid=draft_superseded_item.table_guid,
        record_history_guid=draft_superseded_item.record_history_guid,
    )
    items = [item]
    admin_client.add_items_to_list(new_list, items)
    return new_list


@pytest.fixture
def new_basic_list(basic_client, request, list_name) -> RecordList:
    """
    Provides the identifier of newly created list.
    The created list include the name of the calling test as a `description`.
    """
    new_list = basic_client.create_list(name=list_name, description=request.node.name)
    cleanup = getattr(request, "param", {}).get("cleanup", True)
    yield new_list
    if cleanup:
        basic_client.delete_list(new_list)


@pytest.fixture
def new_basic_list_with_one_unreleased_item(
    basic_client, new_basic_list, unreleased_item
) -> RecordList:
    items = [unreleased_item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_unreleased_item_by_history(
    basic_client, new_basic_list, unreleased_item
) -> RecordList:
    item = RecordListItem(
        database_guid=unreleased_item.database_guid,
        table_guid=unreleased_item.table_guid,
        record_history_guid=unreleased_item.record_history_guid,
    )
    items = [item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_released_item(
    basic_client, new_basic_list, released_item
) -> RecordList:
    items = [released_item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_released_item_by_history(
    basic_client, new_basic_list, released_item
) -> RecordList:
    item = RecordListItem(
        database_guid=released_item.database_guid,
        table_guid=released_item.table_guid,
        record_history_guid=released_item.record_history_guid,
    )
    items = [item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_superseded_item(
    basic_client, new_basic_list, superseded_item
) -> RecordList:
    items = [superseded_item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_superseded_item_by_history(
    basic_client, new_basic_list, superseded_item
) -> RecordList:
    item = RecordListItem(
        database_guid=superseded_item.database_guid,
        table_guid=superseded_item.table_guid,
        record_history_guid=superseded_item.record_history_guid,
    )
    items = [item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_draft_superseded_item(
    basic_client, new_basic_list, draft_superseded_item
) -> RecordList:
    items = [draft_superseded_item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_draft_superseded_item_by_history(
    basic_client, new_basic_list, draft_superseded_item
) -> RecordList:
    item = RecordListItem(
        database_guid=draft_superseded_item.database_guid,
        table_guid=draft_superseded_item.table_guid,
        record_history_guid=draft_superseded_item.record_history_guid,
    )
    items = [item]
    basic_client.add_items_to_list(new_basic_list, items)
    return new_basic_list


@pytest.fixture(scope="function")
def cleanup_admin(admin_client) -> List[RecordList]:
    to_delete = []
    yield to_delete
    for record_list in to_delete:
        admin_client.delete_list(record_list)


@pytest.fixture(scope="function")
def cleanup_basic(basic_client) -> List[RecordList]:
    to_delete = []
    yield to_delete
    for record_list in to_delete:
        basic_client.delete_list(record_list)
