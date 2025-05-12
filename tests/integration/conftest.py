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

import os
from typing import List
from unittest.mock import Mock
import uuid

from ansys.grantami.serverapi_openapi.v2025r2.api import (
    SchemaDatabasesApi,
    SchemaTablesApi,
    SearchApi,
)
from ansys.grantami.serverapi_openapi.v2025r2.models import (
    GsaBooleanCriterion,
    GsaDiscreteTextValuesDatumCriterion,
    GsaRecordPropertyCriterion,
    GsaSearchableRecordProperty,
    GsaSearchRequest,
    GsaShortTextDatumCriterion,
    GsaTextMatchBehavior,
    GsaVersionState,
)
from common import (
    DB_KEY,
    DB_KEY_RS,
    DEISGN_DATA_TABLE_NAME,
    TENSILE_STATISTICAL_DATA_TABLE_NAME,
    RecordCreator,
)
import pytest

from ansys.grantami.recordlists import Connection, RecordList, RecordListItem, RecordListsApiClient
from ansys.grantami.recordlists._connection import _ClientFactory


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
    sl_url, list_admin_username, list_admin_password, list_name, mi_version
) -> RecordListsApiClient:
    """
    Fixture providing a real ApiClient to run integration tests against an instance of Granta MI
    Server API.
    On teardown, deletes all lists named using the fixture `list_name`.
    """
    connection = Connection(sl_url).with_credentials(list_admin_username, list_admin_password)
    try:
        client = connection.connect()
    except ConnectionError as e:
        if mi_version not in _ClientFactory(Mock(spec=Connection))._client_map:
            pytest.skip(
                f"Client not available for Granta MI v{'.'.join(str(v) for v in mi_version)}"
            )
        else:
            raise e

    yield client

    all_lists = client.get_all_lists()
    for record_list in all_lists:
        if list_name in record_list.name:
            client.delete_list(record_list)


@pytest.fixture(scope="session")
def basic_client(
    sl_url, list_username_no_permissions, list_password_no_permissions, list_name, mi_version
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
    try:
        client = connection.connect()
    except ConnectionError as e:
        if mi_version not in _ClientFactory(Mock(spec=Connection))._client_map:
            pytest.skip(
                f"Client not available for Granta MI v{'.'.join(str(v) for v in mi_version)}"
            )
        else:
            raise e

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
def training_database_guid(admin_client) -> str:
    schema_api = SchemaDatabasesApi(admin_client)
    dbs = schema_api.get_all_databases()
    return next(db.guid for db in dbs.databases if db.key == DB_KEY)


@pytest.fixture(scope="session")
def design_data_table_guid(admin_client) -> str:
    table_api = SchemaTablesApi(admin_client)
    table_response = table_api.get_tables(database_key=DB_KEY)
    return next(
        table.guid for table in table_response.tables if table.name == DEISGN_DATA_TABLE_NAME
    )


@pytest.fixture(scope="session")
def tensile_statistical_data_table_guid(admin_client) -> str:
    table_api = SchemaTablesApi(admin_client)
    table_response = table_api.get_tables(database_key=DB_KEY)
    return next(
        table.guid
        for table in table_response.tables
        if table.name == TENSILE_STATISTICAL_DATA_TABLE_NAME
    )


@pytest.fixture(scope="session")
def resolvable_items(admin_client, training_database_guid) -> List[RecordListItem]:
    """Get all records in the MI_Training database and use them to create
    a list of RecordListItems which can be added to a list.

    Exclude records in the 'Tensile Test Data' table, since this is used in the
    grantami-jobqueue integration tests, and the changing contents of the table
    can cause test failures.
    """
    search_api = SearchApi(admin_client)

    is_any_record_type = GsaRecordPropertyCriterion(
        _property=GsaSearchableRecordProperty.RECORDTYPE,
        inner_criterion=GsaDiscreteTextValuesDatumCriterion(
            any=["Record", "Generic", "Folder"],
        ),
    )
    is_in_tensile_test_data_table = GsaRecordPropertyCriterion(
        _property=GsaSearchableRecordProperty.TABLENAME,
        inner_criterion=GsaShortTextDatumCriterion(
            text_match_behavior=GsaTextMatchBehavior.EXACTMATCH,
            value="Tensile Test Data",
        ),
    )

    search_body = GsaSearchRequest(
        criterion=GsaBooleanCriterion(
            all=[is_any_record_type],
            _none=[is_in_tensile_test_data_table],
        )
    )
    search_results = search_api.database_search(
        database_key=DB_KEY,
        body=search_body,
    )
    return [
        RecordListItem(
            training_database_guid,
            result.table_guid,
            result.record_history_guid,
        )
        for result in search_results.results
    ]


@pytest.fixture(scope="session")
def resolvable_items_without_table_guids(resolvable_items) -> List[RecordListItem]:
    return [
        RecordListItem(
            database_guid=item.database_guid,
            table_guid=None,
            record_history_guid=item.record_history_guid,
        )
        for item in resolvable_items
    ]


@pytest.fixture(scope="session")
def rs_database_guid(admin_client) -> str:
    schema_api = SchemaDatabasesApi(admin_client)
    dbs = schema_api.get_all_databases()
    return next(db.guid for db in dbs.databases if db.key == DB_KEY_RS)


@pytest.fixture(scope="session")
def resolvable_rs_items(admin_client, rs_database_guid) -> List[RecordListItem]:
    """Get all records in the MI_Restricted_Substances database and use them to create
    a list of RecordListItems which can be added to a list.
    """
    search_api = SearchApi(admin_client)

    is_any_record_type = GsaRecordPropertyCriterion(
        _property=GsaSearchableRecordProperty.RECORDTYPE,
        inner_criterion=GsaDiscreteTextValuesDatumCriterion(
            any=["Record", "Generic", "Folder"],
        ),
    )
    search_body = GsaSearchRequest(
        criterion=GsaBooleanCriterion(
            all=[is_any_record_type],
        )
    )
    search_results = search_api.database_search(
        database_key=DB_KEY_RS,
        body=search_body,
    )
    return [
        RecordListItem(
            rs_database_guid,
            result.table_guid,
            result.record_history_guid,
        )
        for result in search_results.results
        if result.database_key == DB_KEY_RS
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
def unreleased_item(admin_client) -> RecordListItem:
    """
    History
    |
    |-- Version 1 (unreleased) *
    """
    record_creator = RecordCreator(admin_client, DB_KEY, DEISGN_DATA_TABLE_NAME, "UnreleasedRecord")
    record_creator.get_or_create_version(GsaVersionState.UNRELEASED, 1)
    return RecordListItem(
        database_guid=record_creator.database_guid,
        table_guid=record_creator.table_guid,
        record_history_guid=record_creator.history_guid,
        record_version=1,
    )


@pytest.fixture(scope="session")
def released_item(admin_client) -> RecordListItem:
    """
    History
    |
    |-- Version 1 (released) *
    """
    record_creator = RecordCreator(admin_client, DB_KEY, DEISGN_DATA_TABLE_NAME, "ReleasedRecord")
    record_creator.get_or_create_version(GsaVersionState.RELEASED, 1)
    return RecordListItem(
        database_guid=record_creator.database_guid,
        table_guid=record_creator.table_guid,
        record_history_guid=record_creator.history_guid,
        record_version=1,
    )


@pytest.fixture(scope="session")
def superseded_item(admin_client) -> RecordListItem:
    """
    History
    |
    |-- Version 1 (superseded) *
    |-- Version 2 (released)
    """
    record_creator = RecordCreator(admin_client, DB_KEY, DEISGN_DATA_TABLE_NAME, "SupersededRecord")
    record_creator.get_or_create_version(GsaVersionState.SUPERSEDED, 1)
    return RecordListItem(
        database_guid=record_creator.database_guid,
        table_guid=record_creator.table_guid,
        record_history_guid=record_creator.history_guid,
        record_version=1,
    )


@pytest.fixture(scope="session")
def draft_superseded_item(admin_client) -> RecordListItem:
    """
    History
    |
    |-- Version 1 (released) *
    |-- Version 2 (unreleased)
    """
    record_creator = RecordCreator(
        admin_client, DB_KEY, DEISGN_DATA_TABLE_NAME, "DraftSupersededRecord"
    )
    record_creator.get_or_create_version(GsaVersionState.RELEASED, 1)
    return RecordListItem(
        database_guid=record_creator.database_guid,
        table_guid=record_creator.table_guid,
        record_history_guid=record_creator.history_guid,
        record_version=1,
    )


@pytest.fixture(scope="session")
def draft_superseding_item(admin_client) -> RecordListItem:
    """
    History
    |
    |-- Version 1 (released)
    |-- Version 2 (unreleased) *
    """
    record_creator = RecordCreator(
        admin_client, DB_KEY, DEISGN_DATA_TABLE_NAME, "DraftSupersededRecord"
    )
    record_creator.get_or_create_version(GsaVersionState.UNRELEASED, 2)
    return RecordListItem(
        database_guid=record_creator.database_guid,
        table_guid=record_creator.table_guid,
        record_history_guid=record_creator.history_guid,
        record_version=2,
    )


@pytest.fixture
def new_admin_list_with_one_unreleased_item(admin_client, new_list, unreleased_item) -> RecordList:
    """
    History
    |
    |-- Version 1 (unreleased) *
    """
    admin_client.add_items_to_list(new_list, [unreleased_item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_unreleased_item_by_history(
    admin_client, new_list, unreleased_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (unreleased) *
    """
    item = RecordListItem(
        database_guid=unreleased_item.database_guid,
        table_guid=unreleased_item.table_guid,
        record_history_guid=unreleased_item.record_history_guid,
    )
    admin_client.add_items_to_list(new_list, [item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_released_item(admin_client, new_list, released_item) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    """
    admin_client.add_items_to_list(new_list, [released_item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_released_item_by_history(
    admin_client, new_list, released_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    """
    item = RecordListItem(
        database_guid=released_item.database_guid,
        table_guid=released_item.table_guid,
        record_history_guid=released_item.record_history_guid,
    )
    admin_client.add_items_to_list(new_list, [item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_superseded_item(admin_client, new_list, superseded_item) -> RecordList:
    """
    History
    |
    |-- Version 1 (superseded) *
    |-- Version 2 (released)
    """
    admin_client.add_items_to_list(new_list, [superseded_item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_superseded_item_by_history(
    admin_client, new_list, superseded_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (superseded) *
    |-- Version 2 (released)
    """
    item = RecordListItem(
        database_guid=superseded_item.database_guid,
        table_guid=superseded_item.table_guid,
        record_history_guid=superseded_item.record_history_guid,
    )
    admin_client.add_items_to_list(new_list, [item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_draft_superseded_item(
    admin_client, new_list, draft_superseded_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    |-- Version 2 (unreleased)
    """
    admin_client.add_items_to_list(new_list, [draft_superseded_item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_draft_superseded_item_by_history(
    admin_client, new_list, draft_superseded_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    |-- Version 2 (unreleased)
    """
    item = RecordListItem(
        database_guid=draft_superseded_item.database_guid,
        table_guid=draft_superseded_item.table_guid,
        record_history_guid=draft_superseded_item.record_history_guid,
    )
    admin_client.add_items_to_list(new_list, [item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_draft_superseding_item(
    admin_client, new_list, draft_superseding_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released)
    |-- Version 2 (unreleased) *
    """
    admin_client.add_items_to_list(new_list, [draft_superseding_item])
    return new_list


@pytest.fixture
def new_admin_list_with_one_draft_superseding_item_by_history(
    admin_client, new_list, draft_superseding_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released)
    |-- Version 2 (unreleased) *
    """
    item = RecordListItem(
        database_guid=draft_superseding_item.database_guid,
        table_guid=draft_superseding_item.table_guid,
        record_history_guid=draft_superseding_item.record_history_guid,
    )
    admin_client.add_items_to_list(new_list, [item])
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
    """
    History
    |
    |-- Version 1 (unreleased) *
    """
    basic_client.add_items_to_list(new_basic_list, [unreleased_item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_unreleased_item_by_history(
    basic_client, new_basic_list, unreleased_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (unreleased) *
    """
    item = RecordListItem(
        database_guid=unreleased_item.database_guid,
        table_guid=unreleased_item.table_guid,
        record_history_guid=unreleased_item.record_history_guid,
    )
    basic_client.add_items_to_list(new_basic_list, [item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_released_item(
    basic_client, new_basic_list, released_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    """
    basic_client.add_items_to_list(new_basic_list, [released_item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_released_item_by_history(
    basic_client, new_basic_list, released_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    """
    item = RecordListItem(
        database_guid=released_item.database_guid,
        table_guid=released_item.table_guid,
        record_history_guid=released_item.record_history_guid,
    )
    basic_client.add_items_to_list(new_basic_list, [item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_superseded_item(
    basic_client, new_basic_list, superseded_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (superseded) *
    |-- Version 2 (released)
    """
    basic_client.add_items_to_list(new_basic_list, [superseded_item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_superseded_item_by_history(
    basic_client, new_basic_list, superseded_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (superseded) *
    |-- Version 2 (released)
    """
    item = RecordListItem(
        database_guid=superseded_item.database_guid,
        table_guid=superseded_item.table_guid,
        record_history_guid=superseded_item.record_history_guid,
    )
    basic_client.add_items_to_list(new_basic_list, [item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_draft_superseded_item(
    basic_client, new_basic_list, draft_superseded_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    |-- Version 2 (unreleased)
    """
    basic_client.add_items_to_list(new_basic_list, [draft_superseded_item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_draft_superseded_item_by_history(
    basic_client, new_basic_list, draft_superseded_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released) *
    |-- Version 2 (unreleased)
    """
    item = RecordListItem(
        database_guid=draft_superseded_item.database_guid,
        table_guid=draft_superseded_item.table_guid,
        record_history_guid=draft_superseded_item.record_history_guid,
    )
    basic_client.add_items_to_list(new_basic_list, [item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_draft_superseding_item(
    basic_client, new_basic_list, draft_superseding_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released)
    |-- Version 2 (unreleased) *
    """
    basic_client.add_items_to_list(new_basic_list, [draft_superseding_item])
    return new_basic_list


@pytest.fixture
def new_basic_list_with_one_draft_superseding_item_by_history(
    basic_client, new_basic_list, draft_superseding_item
) -> RecordList:
    """
    History
    |
    |-- Version 1 (released)
    |-- Version 2 (unreleased) *
    """
    item = RecordListItem(
        database_guid=draft_superseding_item.database_guid,
        table_guid=draft_superseding_item.table_guid,
        record_history_guid=draft_superseding_item.record_history_guid,
    )
    basic_client.add_items_to_list(new_basic_list, [item])
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


@pytest.fixture(autouse=True)
def process_integration_marks(request, mi_version):
    """Processes the arguments provided to the integration mark.

    If the mark is initialized with the kwarg ``mi_versions``, the value must be of type list[tuple[int, int]], where
    the tuples contain compatible major and minor release versions of Granta MI. If the version is specified for a test
    case and the Granta MI version being tested against is not in the provided list, the test case is skipped.

    Also handles test-specific behavior, for example if a certain Granta MI version and test are incompatible and need
    to be skipped or xfailed.
    """

    # Argument validation
    if not request.node.get_closest_marker("integration"):
        # No integration marker anywhere in the stack
        return

    if mi_version is None:
        # We didn't get an MI version. If integration tests were requested, an MI version must be provided. Raise
        # an exception to fail all integration tests.
        raise ValueError(
            "No Granta MI Version provided to pytest. Specify Granta MI version with --mi-version MAJOR.MINOR."
        )

    # Process integration mark arguments
    mark: pytest.Mark = request.node.get_closest_marker("integration")
    if not mark.kwargs:
        # Mark not initialized with any keyword arguments
        return
    allowed_versions = mark.kwargs.get("mi_versions")
    if allowed_versions is None:
        return
    if not isinstance(allowed_versions, list):
        raise TypeError("mi_versions argument type must be of type 'list'")
    if mi_version not in allowed_versions:
        formatted_version = ".".join(str(x) for x in mi_version)
        skip_message = f'Test skipped for Granta MI release version "{formatted_version}"'
        pytest.skip(skip_message)
