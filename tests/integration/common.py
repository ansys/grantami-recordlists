from typing import Optional, Tuple

from ansys.grantami.serverapi_openapi.api import (
    RecordsRecordHistoriesApi,
    RecordsRecordVersionsApi,
    SearchApi,
)
from ansys.grantami.serverapi_openapi.models import (
    GrantaServerApiRecordsRecordHistoriesCreateRecordHistory,
    GrantaServerApiRecordType,
    GrantaServerApiSearchRecordPropertyCriterion,
    GrantaServerApiSearchSearchableRecordProperty,
    GrantaServerApiSearchSearchRequest,
    GrantaServerApiSearchShortTextDatumCriterion,
    GrantaServerApiVersionState,
)

DB_KEY = "MI_Training"
TABLE_NAME = "Design Data"


def ensure_history_exists(admin_client, table_guid, history_name: str) -> str:
    """Check that a history with the specified name exists in the root of the table.

    If the history already exists, just return it. If not, create it and then return it.

    Parameters
    ----------
    admin_client : RecordListsApiClient
        Client to use for searching and record history creation
    table_guid : str
        GUID of the table to create the new history in
    history_name : str
        Name of the new history to create

    Returns
    -------
    str
        The record history GUID
    """

    # First check if we can find the record
    search_api = SearchApi(admin_client)
    search_body = GrantaServerApiSearchSearchRequest(
        criterion=GrantaServerApiSearchRecordPropertyCriterion(
            _property=GrantaServerApiSearchSearchableRecordProperty.RECORDNAME,
            inner_criterion=GrantaServerApiSearchShortTextDatumCriterion(
                value=history_name,
            ),
        )
    )
    search_results = search_api.database_search(
        database_key=DB_KEY,
        body=search_body,
    )
    # If we got exactly one hit, return it
    record_count = len(search_results.results)
    if record_count == 1:
        return search_results.results[0].record_history_guid
    elif record_count > 1:
        raise RuntimeError(
            f"Too many records found in database with name {history_name}. Found "
            f"{record_count}, but expected 0 or 1. Cannot continue."
        )

    history_api = RecordsRecordHistoriesApi(admin_client)
    response = history_api.create_record_history(
        database_key=DB_KEY,
        table_guid=table_guid,
        body=GrantaServerApiRecordsRecordHistoriesCreateRecordHistory(
            name=history_name, record_type=GrantaServerApiRecordType.RECORD
        ),
    )
    return response.guid


def get_latest_version_info(
    admin_client, history_guid: str
) -> Tuple[GrantaServerApiVersionState, str, int]:
    """Get information about the latest version of a specified record history.

    Parameters
    ----------
    admin_client : RecordListsApiClient
        Client to use for searching and record history creation
    history_guid : str
        GUID of the history to get information for

    Returns
    -------
    Tuple[GrantaServerApiVersionState, str, int]
        A tuple of the record version state, the version guid, and the version number
    """
    history_api = RecordsRecordHistoriesApi(admin_client)
    history_details = history_api.get_record_history(
        database_key=DB_KEY,
        record_history_guid=history_guid,
    )
    return (
        history_details.record_versions[-1].version_state,
        history_details.record_versions[-1].guid,
        history_details.record_versions[-1].version_number,
    )


def get_version_info_in_state(
    admin_client,
    history_guid: str,
    version_state: GrantaServerApiVersionState,
    version_number: Optional[int] = None,
) -> Tuple[GrantaServerApiVersionState, str, int]:
    """Get information about a specific version of a record history.

    Parameters
    ----------
    admin_client : RecordListsApiClient
        Client to use for searching and record history creation
    history_guid : str
        GUID of the history to get information for
    version_state : RecordVersionState
        The state of the required version
    version_number : Optional[int]
        The version number of the required version

    Returns
    -------
    Tuple[GrantaServerApiVersionState, str, int]
        A tuple of the record version state, the version guid, and the version number

    Raises
    ------
    ValueError
        If a record version meeting the required state and version number cannot be found for the
        specified history.
    """
    history_api = RecordsRecordHistoriesApi(admin_client)
    history_details = history_api.get_record_history(
        database_key=DB_KEY,
        record_history_guid=history_guid,
    )
    for version in history_details.record_versions:
        if version.version_state == version_state and (
            version_number is None or version_number == version.version_number
        ):
            return (
                version.version_state,
                version.guid,
                version.version_number,
            )
    error_message = f"No record version found in state {version_state}"
    if version_number is None:
        error_message = f"{error_message} and with version number {version_number}"
    raise ValueError(error_message)


def release_version(admin_client, table_guid: str, history_guid: str, version_guid: str) -> None:
    """Release the unreleased version guid.

    Parameters
    ----------
    admin_client : RecordListsApiClient
        Client to use for searching and record history creation
    table_guid : str
        GUID of the table containing the history
    history_guid : str
        The history guid of the record to be released
    version_guid : str
        The version guid of the version to be released

    Raises
    ------
    RuntimeError
        If an error occurs when releasing the record.
    """
    versions_api = RecordsRecordVersionsApi(admin_client)
    result = versions_api.release_record_version(
        database_key=DB_KEY,
        table_guid=table_guid,
        record_history_guid=history_guid,
        record_version_guid=version_guid,
    )
    try:
        raise RuntimeError(result.errors)
    except AttributeError:
        pass


def create_new_unreleased_version(
    admin_client, table_guid: str, history_guid: str, version_guid: str
) -> str:
    """Create a new unreleased version of an existing history.

    Parameters
    ----------
    admin_client : RecordListsApiClient
        Client to use for searching and record history creation
    table_guid : str
        GUID of the table containing the history
    history_guid : str
        The history guid of the record to be released
    version_guid : str
        The version guid of the version to be released

    Returns
    -------
    str
        The version GUID of the new unreleased record version.

    Raises
    ------
    RuntimeError
        If an error occurs when creating a new unreleased version.
    """
    versions_api = RecordsRecordVersionsApi(admin_client)
    result = versions_api.get_modifiable_record_version(
        database_key=DB_KEY,
        table_guid=table_guid,
        record_history_guid=history_guid,
        record_version_guid=version_guid,
    )
    try:
        raise RuntimeError(result.errors)
    except AttributeError:
        pass
    return result.guid


def supersede_version(admin_client, table_guid: str, history_guid: str, version_guid: str) -> None:
    """Create a new unreleased version of an existing history and release it, thus superseding
    the original record.

    Parameters
    ----------
    admin_client : RecordListsApiClient
        Client to use for searching and record history creation
    table_guid : str
        GUID of the table containing the history
    history_guid : str
        The history guid of the record to be released
    version_guid : str
        The version guid of the version to be released

    Raises
    ------
    RuntimeError
        If an error occurs when superseding the record version.
    """
    new_version = create_new_unreleased_version(
        admin_client,
        table_guid=table_guid,
        history_guid=history_guid,
        version_guid=version_guid,
    )
    release_version(
        admin_client,
        table_guid=table_guid,
        history_guid=history_guid,
        version_guid=new_version,
    )
