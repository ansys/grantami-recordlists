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

from collections import defaultdict
import concurrent.futures
import functools
from typing import Iterator, List, Optional, Tuple, Union

from ansys.grantami.serverapi_openapi.v2025r2 import api, models
from ansys.openapi.common import (
    ApiClient,
    ApiClientFactory,
    ApiException,
    SessionConfiguration,
    Unset,
    Unset_Type,
    generate_user_agent,
)
import requests  # type: ignore[import-untyped]

from ._logger import logger
from ._models import (
    AuditLogItem,
    AuditLogSearchCriterion,
    BooleanCriterion,
    RecordList,
    RecordListItem,
    SearchCriterion,
    SearchResult,
    _PagedResult,
)

PROXY_PATH = "/proxy/v1.svc/mi"
AUTH_PATH = "/Health/v2.svc"
API_DEFINITION_PATH = "/swagger/v1/swagger.json"
GRANTA_APPLICATION_NAME_HEADER = "PyGranta RecordLists"

MINIMUM_GRANTA_MI_VERSION = (24, 2)
CURRENT_GRANTA_MI_VERSION = (25, 2)

_ArgNotProvided = "_ArgNotProvided"


class RecordListsApiClient(ApiClient):
    """
    Communicates with Granta MI.

    This class is instantiated by the
    :class:`Connection` class and should not be instantiated
    directly.
    """

    def __init__(
        self,
        session: requests.Session,
        service_layer_url: str,
        configuration: SessionConfiguration,
    ):
        self._service_layer_url = service_layer_url
        api_url = service_layer_url + PROXY_PATH

        logger.debug("Creating RecordListsApiClient")
        logger.debug(f"Base Service Layer URL: {self._service_layer_url}")
        logger.debug(f"Service URL: {api_url}")

        super().__init__(session, api_url, configuration)
        self.list_management_api = api.ListManagementApi(self)
        self.list_item_api = api.ListItemApi(self)
        self.list_permissions_api = api.ListPermissionsApi(self)
        self.list_audit_log_api = api.ListAuditLogApi(self)
        self.schema_api = api.SchemaApi(self)
        self._models = models

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} url: {self._service_layer_url}>"

    def _get_mi_server_version(self) -> Tuple[int, ...]:
        """Get the Granta MI version as a tuple.

        Makes direct use of the underlying serverapi-openapi package. The API methods
        in this package may change over time, and so it is expected that this method
        will grow to support multiple versions of the serverapi-openapi package.

        Parameters
        ----------
        client : :class:`~.RecordListApiClient`
            Client object.

        Returns
        -------
        tuple of int
            Granta MI version number.
        """
        server_version_response = self.schema_api.get_version()
        server_version = server_version_response.version
        assert server_version
        parsed_version = tuple([int(e) for e in server_version.split(".")])
        return parsed_version

    def _get_mi_compatibility_version(self) -> Tuple[int, int]:
        full_version = self._get_mi_server_version()
        return full_version[0], full_version[1]

    def get_all_lists(self) -> List[RecordList]:
        """
        Get the details of all record lists available for the current user.

        Performs an HTTP request against the Granta MI Server API.

        Returns
        -------
        list of :class:`.RecordList`
            List of available record lists.
        """
        logger.info(f"Getting all lists available with connection {self}")
        record_lists = self.list_management_api.get_all_lists()
        assert record_lists is not None
        return [RecordList._from_model(record_list) for record_list in record_lists.lists]

    def get_list(self, identifier: str) -> RecordList:
        """
        Get the details of a record list.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        :class:`.RecordList`
        """
        logger.info(f"Getting list with identifier {identifier} with connection {self}")
        record_list = self.list_management_api.get_list(list_identifier=identifier)
        assert record_list is not None
        return RecordList._from_model(record_list)

    def search_for_lists(
        self, criterion: Union[BooleanCriterion, SearchCriterion], include_items: bool = False
    ) -> List[SearchResult]:
        """
        Search for record lists matching the provided criteria.

        Performs multiple HTTP requests against the Server API.

        Parameters
        ----------
        criterion : :class:`.SearchCriterion` | :class:`.BooleanCriterion`
            Criterion to use to filter lists.
        include_items: bool
            Whether the search results should include record list items.

        Returns
        -------
        list of :class:`.SearchResult`
            List of record lists matching the provided criterion.
        """
        logger.info(f"Searching for lists with connection {self}")
        response_options = self._models.GsaResponseOptions(
            include_record_list_items=include_items,
        )
        search_info = self.list_management_api.run_record_lists_search(
            body=self._models.GsaRecordListSearchRequest(
                search_criterion=criterion._to_model(),
                response_options=response_options,
            )
        )
        assert search_info is not None
        search_results = self.list_management_api.get_record_list_search_results(
            result_resource_identifier=search_info.search_result_identifier
        )
        assert search_results is not None
        return [
            SearchResult._from_model(search_result, include_items)
            for search_result in search_results.search_results
        ]

    def get_list_items(self, record_list: RecordList) -> List[RecordListItem]:
        """
        Get all items included in a record list.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        record_list : RecordList
            Record list for which items will be fetched.

        Returns
        -------
        list of :class:`.RecordListItem`
            List of items included in the record list.
        """
        logger.info(f"Getting items in list {record_list} with connection {self}")
        items_response = self.list_item_api.get_list_items(list_identifier=record_list.identifier)
        assert items_response is not None
        return [RecordListItem._from_model(item) for item in items_response.items]

    def get_resolvable_list_items(
        self, record_list: RecordList, read_mode: bool = False
    ) -> List[RecordListItem]:
        """
        Get all resolvable items included in a record list.

        If an item cannot be resolved, it will not be returned. Performs multiple HTTP requests
        against the Granta MI Server API.

        .. versionadded:: 1.2

        Parameters
        ----------
        record_list : RecordList
            Record list for which items will be fetched.
        read_mode : bool
            Whether to enable read-mode for users who ordinarily have write permissions. Has no
            effect for read-only users.

        Returns
        -------
        list of :class:`.RecordListItem`
            List of items included in the record list.

        Notes
        -----
        Whether an item can be resolved depends on the role the user has on the Granta MI server. As
        a brief summary:

        * If the item doesn't specify a version, this method tests if the user can access either the
          record or, if in a version-controlled table, a version of the record in any state. A
          record cannot be resolved if:

          * It has been deleted
          * It has been withdrawn and the user is a read user (version-controlled tables only)
          * It only has one unreleased version and the user is a read user (version-controlled
            tables only)
          * It is hidden by access control

        * If the item specifies a version, this method tests if the user can access that specific
          version of the record. This condition only applies to version-controlled tables. A
          record version cannot be resolved if:

          * It is unreleased and the user is a read user
          * It has been withdrawn and the user is a read user
          * It is hidden by access control

        Since version control and access control is intended to allow and restrict access to records
        for certain groups of users, this method may return different results for different users
        depending on the configuration of Granta MI.
        """
        all_items = self.get_list_items(record_list)
        logger.info("Testing if retrieved items are resolvable")
        resolver = _ItemResolver(self, read_mode=read_mode)
        return resolver.get_resolvable_items(all_items)

    def add_items_to_list(
        self, record_list: RecordList, items: List[RecordListItem]
    ) -> List[RecordListItem]:
        """
        Add items to a record list.

        Performs an HTTP request against the Granta MI Server API.
        Items are not validated against existing records on the server or existing items in the
        list.

        Parameters
        ----------
        record_list : RecordList
            Record list in which items will be added.
        items : list of :class:`.RecordListItem`
            List of items to add to the record list.

        Returns
        -------
        list of :class:`.RecordListItem`
           List of items included in the record list.
        """
        logger.info(f"Adding {len(items)} items to list {record_list} with connection {self}")
        response_items = self.list_item_api.add_items_to_list(
            list_identifier=record_list.identifier,
            body=self._models.GsaCreateRecordListItemsInfo(
                items=[item._to_create_list_item_model() for item in items]
            ),
        )
        assert response_items is not None
        return [RecordListItem._from_model(item) for item in response_items.items]

    def remove_items_from_list(
        self, record_list: RecordList, items: List[RecordListItem]
    ) -> List[RecordListItem]:
        """
        Remove items from a record list.

        Performs an HTTP request against the Granta MI Server API.
        Attempting to remove items that are not in the list will not result in an error.

        Parameters
        ----------
        record_list : RecordList
            Record list from which items will be removed.
        items : list of :class:`.RecordListItem`
            List of items to remove from the record list.

        Returns
        -------
        list of :class:`.RecordListItem`
           List of items included in the record list.
        """
        logger.info(f"Removing {len(items)} items from list {record_list} with connection {self}")
        response_items = self.list_item_api.remove_items_from_list(
            list_identifier=record_list.identifier,
            body=self._models.GsaDeleteRecordListItems(
                items=[item._to_delete_list_item_model() for item in items]
            ),
        )
        assert response_items is not None
        return [RecordListItem._from_model(item) for item in response_items.items]

    def create_list(
        self,
        name: str,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        items: Optional[List[RecordListItem]] = None,
    ) -> RecordList:
        """
        Create a new record list with the provided arguments.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        name : str
            Name of the record list.
        description : str or None
            Description of the record list.
        notes : str or None
            Notes of the record list.
        items : list of :class:`.RecordListItem` or None
            List of items to add to the record list.

        Returns
        -------
        :class:`.RecordList`
            Created record list details.
        """
        items_string = "no items" if items is None or len(items) == 0 else f"{len(items)} items"
        logger.info(f"Creating new list {name} with {items_string} with connection {self}")
        _items: models.GsaCreateRecordListItemsInfo | Unset_Type
        if items is not None:
            _items = self._models.GsaCreateRecordListItemsInfo(
                items=[list_item._to_create_list_item_model() for list_item in items]
            )
        else:
            _items = Unset
        body = self._models.GsaCreateRecordList(
            name=name, description=description, notes=notes, items=_items
        )
        created_list = self.list_management_api.create_list(body=body)
        assert created_list is not None
        return RecordList._from_model(created_list)

    def delete_list(self, record_list: RecordList) -> None:
        """
        Delete a record list.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        record_list : RecordList
            Record list to delete.
        """
        logger.info(f"Removing list {record_list} with connection {self}")
        self.list_management_api.delete_list(list_identifier=record_list.identifier)

    def update_list(
        self,
        record_list: RecordList,
        *,
        name: str = _ArgNotProvided,
        description: Union[str, None] = _ArgNotProvided,
        notes: Union[str, None] = _ArgNotProvided,
    ) -> RecordList:
        """
        Update a record list with the provided arguments.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        record_list : RecordList
            Record list to update.
        name : str, optional
            New value for the name of the record list.
        description : str or None, optional
            New value for the description of the record list. Set to None to delete an existing
            value.
        notes : str or None, optional
            New value for the notes of the record list. Set to None to delete an existing value.

        Returns
        -------
        :class:`.RecordList`
            Updated representation of the record list.
        """
        logger.info(f"Updating list {record_list} with connection {self}")
        if name == _ArgNotProvided and description == _ArgNotProvided and notes == _ArgNotProvided:
            raise ValueError(
                f"Update must include at least one property to update. "
                f"Supported properties are 'name', 'description', and 'notes'."
            )

        if name is None:
            raise ValueError(f"If provided, argument 'name' cannot be None.")

        body = self._models.GsaUpdateRecordListProperties()
        if name != _ArgNotProvided:
            body.name = name
        if description != _ArgNotProvided:
            body.description = description
        if notes != _ArgNotProvided:
            body.notes = notes
        updated_resource = self.list_management_api.update_list(
            list_identifier=record_list.identifier, body=body
        )
        assert updated_resource is not None
        return RecordList._from_model(updated_resource)

    def copy_list(self, record_list: RecordList) -> RecordList:
        """
        Create a copy of a record list.

        Performs an HTTP request against the Granta MI Server API. The resulting list has a name
        prefixed by the original list name.

        Parameters
        ----------
        record_list : RecordList
            Record list to copy.

        Returns
        -------
        :class:`.RecordList`
            Record list created by the copy operation.
        """
        logger.info(f"Copying list {record_list} with connection {self}")
        list_copy = self.list_management_api.copy_list(list_identifier=record_list.identifier)
        assert list_copy is not None
        return RecordList._from_model(list_copy)

    def revise_list(self, record_list: RecordList) -> RecordList:
        """
        Revise a record list.

        Performs an HTTP request against the Granta MI Server API.
        Revising a list allows a user to create a personal copy of a published list and to modify
        its items or details. When the 'in-revision' list is published, it overwrites the original
        list.

        Parameters
        ----------
        record_list : RecordList
            Record list to revise.

        Returns
        -------
        :class:`.RecordList`
            Record list created by the revision operation.
        """
        logger.info(f"Creating revision of list {record_list} with connection {self}")
        list_revision = self.list_management_api.revise_list(
            list_identifier=record_list.identifier,
        )
        assert list_revision is not None
        return RecordList._from_model(list_revision)

    def request_list_approval(self, record_list: RecordList) -> RecordList:
        """
        Request approval for a record list.

        Performs an HTTP request against the Granta MI Server API.
        Requesting approval updates the ``awaiting approval`` status of the record list to ``True``.

        Parameters
        ----------
        record_list : RecordList
            Record list for which approval is requested.

        Returns
        -------
        :class:`.RecordList`
            Updated representation of the record list.
        """
        logger.info(f"Requesting approval for list {record_list} with connection {self}")
        updated_list = self.list_management_api.request_approval(
            list_identifier=record_list.identifier,
        )
        assert updated_list is not None
        return RecordList._from_model(updated_list)

    def publish_list(self, record_list: RecordList) -> RecordList:
        """
        Publish a record list.

        Performs an HTTP request against the Granta MI Server API.
        The list must be awaiting approval and not published already. Publishing the list updates
        the status to *published* and resets the awaiting approval status.
        Published lists can be viewed by all users and cannot be modified. To modify a published
        list, use :meth:`.revise_list`.

        Parameters
        ----------
        record_list : RecordList
            Record list to publish.

        Returns
        -------
        :class:`.RecordList`
            Updated representation of the record list.
        """
        logger.info(f"Publishing list {record_list} with connection {self}")
        updated_list = self.list_management_api.publish_list(
            list_identifier=record_list.identifier,
        )
        assert updated_list is not None
        return RecordList._from_model(updated_list)

    def unpublish_list(self, record_list: RecordList) -> RecordList:
        """
        Withdraw a record list.

        Performs an HTTP request against the Granta MI Server API.
        The list must be published and awaiting approval. Withdrawing the list updates
        the *published* status to False and resets the awaiting approval status.
        All existing subscriptions will be lost on withdrawal.

        Parameters
        ----------
        record_list : RecordList
            Record list to unpublish.

        Returns
        -------
        :class:`.RecordList`
            Updated representation of the record list.
        """
        logger.info(f"Withdrawing list {record_list} with connection {self}")
        updated_list = self.list_management_api.unpublish_list(
            list_identifier=record_list.identifier,
        )
        assert updated_list is not None
        return RecordList._from_model(updated_list)

    def cancel_list_approval_request(self, record_list: RecordList) -> RecordList:
        """
        Cancel a pending request for approval on a record list.

        Performs an HTTP request against the Granta MI Server API.
        The list must be awaiting approval. Cancelling the approval request resets the awaiting
        approval status to False.

        Parameters
        ----------
        record_list : RecordList
            Record list for which to cancel the approval request.

        Returns
        -------
        :class:`.RecordList`
            Updated representation of the record list.
        """
        logger.info(f"Cancelling request to approve list {record_list} with connection {self}")
        updated_list = self.list_management_api.reset_awaiting_approval(
            list_identifier=record_list.identifier,
        )
        assert updated_list is not None
        return RecordList._from_model(updated_list)

    def subscribe_to_list(self, record_list: RecordList) -> None:
        """
        Subscribe the current user to a record list.

        Performs an HTTP request against the Granta MI Server API.
        The list must be published.

        Parameters
        ----------
        record_list : RecordList
            Record list to subscribe to.

        Returns
        -------
        None
        """
        self.list_permissions_api.subscribe(list_identifier=record_list.identifier)

    def unsubscribe_from_list(self, record_list: RecordList) -> None:
        """
        Unsubscribe the current user from a record list.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        record_list : RecordList
            Record list to unsubscribe from.

        Returns
        -------
        None
        """
        self.list_permissions_api.unsubscribe(
            list_identifier=record_list.identifier,
        )

    def get_all_audit_log_entries(self, page_size: Optional[int] = 100) -> Iterator[AuditLogItem]:
        """
        Fetch all audit log entries that are visible to the current user.

        Performs an HTTP request against the Granta MI Server API.

        .. versionadded:: 2.0

        Parameters
        ----------
        page_size : int, optional (default: 100)
            If None then all results will be fetched in one request, this may be a slow operation. If set to
            an int value then the results will be fetched in batches of size `page_size`.

        Returns
        -------
        Iterator of :class:`.AuditLogItem`
            Audit log entries.
        """
        criterion = AuditLogSearchCriterion()
        return self.search_for_audit_log_entries(criterion=criterion, page_size=page_size)

    def search_for_audit_log_entries(
        self, criterion: AuditLogSearchCriterion, page_size: Optional[int] = 100
    ) -> Iterator[AuditLogItem]:
        """
        Fetch audit log entries, filtered by a search criterion.

        Performs an HTTP request against the Granta MI Server API.

        .. versionadded:: 2.0

        Parameters
        ----------
        criterion : AuditLogSearchCriterion
            Criterion by which to filter audit log entries.
        page_size : int, optional (default: 100)
            If None then all results will be fetched in one request, this may be a slow operation. If set to
            an int value then the results will be fetched in batches of size `page_size`.

        Returns
        -------
        Iterator of :class:`.AuditLogItem`
            Audit log entries.
        """
        logger.info("Fetching list audit log entries...")

        if page_size is not None:
            logger.info(
                f"Paging options were specified, fetching in batches of size {page_size}..."
            )

            def get_next_page(
                client: "RecordListsApiClient",
                criterion: models.GsaListAuditLogSearchRequest,
                page_size: int,
                start_index: int,
            ) -> List[AuditLogItem]:
                paging_options = self._models.GsaListsPagingOptions(
                    page_size=page_size, start_index=start_index
                )
                criterion.paging_options = paging_options

                response = client.list_audit_log_api.run_list_audit_log_search(body=criterion)
                assert response is not None
                page_id = response.search_result_identifier
                logger.info(f"Received page with id {page_id}")

                results = client.list_audit_log_api.get_list_audit_log_search_results(
                    result_resource_identifier=page_id,
                )
                assert results is not None
                return [AuditLogItem._from_model(item) for item in results]

            partial_func = functools.partial(get_next_page, self, criterion._to_model())
            return _PagedResult(partial_func, AuditLogItem, page_size)

        logger.info("No paging options were specified, fetching all results...")
        gsa_criterion = criterion._to_model()
        response = self.list_audit_log_api.run_list_audit_log_search(body=gsa_criterion)
        assert response is not None
        result_id = response.search_result_identifier
        logger.info(f"Received result with id {result_id}")

        search_result = self.list_audit_log_api.get_list_audit_log_search_results(
            result_resource_identifier=result_id
        )
        assert search_result is not None
        return iter(AuditLogItem._from_model(item) for item in search_result)


class RecordLists2025R12024R2ApiClient(RecordListsApiClient):
    """
    Communicates with Granta MI.

    Compatibility version for Granta MI 2025 R1 and 2024 R2.

    This class is instantiated by the
    :class:`Connection` class and should not be instantiated
    directly.
    """
    def __init__(
        self,
        session: requests.Session,
        service_layer_url: str,
        configuration: SessionConfiguration,
    ):
        super().__init__(session, service_layer_url, configuration)

        from ansys.grantami.serverapi_openapi.v2025r1 import api, models

        # Type ignore statements below essentially disable type checking across Server API versions
        self.list_management_api = api.ListManagementApi(self)  # type: ignore[assignment]
        self.list_item_api = api.ListItemApi(self)  # type: ignore[assignment]
        self.list_permissions_api = api.ListPermissionsApi(self)  # type: ignore[assignment]
        self.list_audit_log_api = None  # type: ignore[assignment]
        self._models = models

    def search_for_lists(
        self, criterion: Union[BooleanCriterion, SearchCriterion], include_items: bool = False
    ) -> List[SearchResult]:
        """
        Search for record lists matching the provided criteria.

        Performs multiple HTTP requests against the Server API.

        Parameters
        ----------
        criterion : :class:`.SearchCriterion` | :class:`.BooleanCriterion`
            Criterion to use to filter lists.
        include_items: bool
            Whether the search results should include record list items.

        Returns
        -------
        list of :class:`.SearchResult`
            List of record lists matching the provided criterion.
        """
        logger.info(f"Searching for lists with connection {self}")
        response_options = models.GsaResponseOptions(
            include_record_list_items=include_items,
        )
        search_info = self.list_management_api.run_record_lists_search(
            body=self._models.GsaRecordListSearchRequest(
                search_criterion=criterion._to_2025r1_model(),
                response_options=response_options,
            )
        )
        assert search_info is not None
        search_results = self.list_management_api.get_record_list_search_results(
            result_resource_identifier=search_info.search_result_identifier
        )
        if not search_results:
            return []
        return [
            SearchResult._from_model(search_result, include_items)
            for search_result in search_results.search_results
        ]


class _ItemResolver:
    _max_requests = 5

    def __init__(self, client: ApiClient, read_mode: bool) -> None:
        self._record_histories_api = api.RecordsRecordHistoriesApi(client)
        self._record_versions_api = api.RecordsRecordVersionsApi(client)
        self._db_schema_api = api.SchemaDatabasesApi(client)
        self._read_mode = read_mode

    def get_resolvable_items(self, all_items: List[RecordListItem]) -> List[RecordListItem]:
        """Test all items to see if they can be resolved as the current user.

        Uses concurrent.futures to handle threading, since openapi-common is currently based on
        requests which limits asyncio options.

        Parameters
        ----------
        all_items
            The items for which to check resolvability.

        Returns
        -------
        resolvable_items
            The items which could be resolved on the server.
        """
        db_map = self._get_db_map()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_requests) as executor:
            resolvable_test_futures = {
                executor.submit(self._is_item_resolvable, i, db_map): i for i in all_items
            }
            resolvable_items = [
                resolvable_test_futures[f]
                for f in concurrent.futures.as_completed(resolvable_test_futures)
                if f.result()
            ]
        return resolvable_items

    def _get_db_map(self) -> defaultdict[str, List[str]]:
        dbs = self._db_schema_api.get_all_databases()
        db_map: defaultdict[str, List[str]] = defaultdict(list)
        if not dbs.databases:
            return db_map
        for db in dbs.databases:
            assert db.guid
            db_map[db.guid].append(db.key)
        return db_map

    def _is_item_resolvable(
        self, item: RecordListItem, db_map: defaultdict[str, List[str]]
    ) -> bool:
        """Test if a specific item is resolvable.

        Returns
        -------
        bool
            True if the item can be resolved in any database with the correct GUID, False otherwise.
        """
        if item.database_guid not in db_map:
            return False
        for db_key in db_map[item.database_guid]:
            if self._is_item_resolvable_in_db(item, db_key):
                return True
        return False

    def _is_item_resolvable_in_db(self, item: RecordListItem, db_key: str) -> bool:
        """
        Test if a specific item is resolvable in a database.

        If the item has a record version and record guid, attempt to resolve the record version
        directly.

        If the item has a record version number only, check that the version number is available
        to the user running the record.

        If there is no version at all, check that the history can be resolved.

        Returns
        -------
        bool
            True if the item can be resolved, False otherwise.
        """
        try:
            if item.record_version is not None and item.record_guid is not None:
                self._record_versions_api.get_record_version(
                    database_key=db_key,
                    table_guid=item.table_guid,
                    record_history_guid=item.record_history_guid,
                    record_version_guid=item.record_guid,
                    mode="read" if self._read_mode else None,
                )
            else:
                history_info = self._record_histories_api.get_record_history(
                    database_key=db_key,
                    record_history_guid=item.record_history_guid,
                    mode="read" if self._read_mode else None,
                )
                if item.record_version is not None and history_info is not None:
                    for version in history_info.record_versions:
                        if item.record_version == version.version_number:
                            return True
                    return False
        except ApiException as e:
            if e.status_code != 404:
                raise
            return False
        else:
            return True


class Connection(ApiClientFactory):
    """
    Connects to a Granta MI ServerAPI instance.

    This is a subclass of the :class:`ansys.openapi.common.ApiClientFactory` class. All methods in
    this class are documented as returning :class:`~ansys.openapi.common.ApiClientFactory` class
    instances of the :class:`ansys.grantami.recordlists.Connection` class instead.

    Parameters
    ----------
    servicelayer_url : str
       Base URL of the Granta MI Service Layer application.
    session_configuration : :class:`~ansys.openapi.common.SessionConfiguration`, optional
       Additional configuration settings for the requests session. The default is ``None``, in which
       case the :class:`~ansys.openapi.common.SessionConfiguration` class with default parameters
       is used.

    Notes
    -----
    For advanced usage, including configuring session-specific properties and timeouts, see the
    :external+openapi-common:doc:`ansys-openapi-common API reference <api/index>`. Specifically, see
    the documentation for the :class:`~ansys.openapi.common.ApiClientFactory` base class and the
    :class:`~ansys.openapi.common.SessionConfiguration` class


    1. Create the connection builder object and specify the server to connect to.
    2. Specify the authentication method to use for the connection and provide credentials if
       required.
    3. Connect to the server, which returns the client object.

    The examples show this process for different authentication methods.

    Examples
    --------
    >>> client = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> client
    <RecordListsApiClient: url=http://my_mi_server/mi_servicelayer>
    >>> client = (
    ...     Connection("http://my_mi_server/mi_servicelayer")
    ...     .with_credentials(username="my_username", password="my_password")
    ...     .connect()
    ... )
    >>> client
    <RecordListsApiClient: url: http://my_mi_server/mi_servicelayer>
    """

    def __init__(
        self, servicelayer_url: str, session_configuration: Optional[SessionConfiguration] = None
    ):
        from . import __version__

        auth_url = servicelayer_url.strip("/") + AUTH_PATH
        super().__init__(auth_url, session_configuration)
        self._base_service_layer_url = servicelayer_url
        self._session_configuration.headers["X-Granta-ApplicationName"] = (
            GRANTA_APPLICATION_NAME_HEADER
        )
        self._session_configuration.headers["User-Agent"] = generate_user_agent(
            "ansys-grantami-recordlists", __version__
        )

    def connect(self) -> RecordListsApiClient:
        """
        Finalize the :class:`.RecordListsApiClient` client and return it for use.

        Authentication must be configured for this method to succeed.

        Returns
        -------
        :class:`.RecordListsApiClient`
            Client object that can be used to connect to Granta MI and interact with the record
            list API.
        """
        self._validate_builder()
        # 2025 R2 bindings introduce new audit log and record-based searching
        client_25r2 = RecordListsApiClient(
            self._session,
            self._base_service_layer_url,
            self._session_configuration,
        )
        client_25r2.setup_client(models)

        # No breaking changes between Server API 2025 R1 and 2024 R2. Use the same client for both.
        client_25r1_24r2 = RecordLists2025R12024R2ApiClient(
            self._session,
            self._base_service_layer_url,
            self._session_configuration,
        )
        from ansys.grantami.serverapi_openapi.v2025r1 import models as v2025r1models

        client_25r1_24r2.setup_client(v2025r1models)

        mi_version_map = {
            (25, 2): client_25r2,
            (25, 1): client_25r1_24r2,
            (24, 2): client_25r1_24r2,
        }

        server_version = None
        for client in mi_version_map.values():
            try:
                server_version = client._get_mi_compatibility_version()
                break
            except KeyError:
                pass
            except ApiException as e:
                self._process_api_exception(e)
            except requests.exceptions.RetryError as e:
                self._process_retry_error(e)

        if server_version is None:
            raise ConnectionError(
                "Cannot check the Granta MI server version. Ensure the Granta MI server version "
                f"is at least {'.'.join([str(e) for e in MINIMUM_GRANTA_MI_VERSION])}."
            )

        try:
            client = mi_version_map[server_version]
        except KeyError:
            if server_version > CURRENT_GRANTA_MI_VERSION:
                client = mi_version_map[CURRENT_GRANTA_MI_VERSION]
            else:
                raise ConnectionError(
                    f"This package requires a more recent Granta MI version. Detected Granta MI server "
                    f"version is {'.'.join([str(e) for e in server_version])}, but this package "
                    f"requires at least {'.'.join([str(e) for e in MINIMUM_GRANTA_MI_VERSION])}. "
                    "Use the pygranta package to install a version compatible with your Granta MI "
                    "server, for example pip install pygranta==2024.1"
                )
        self._test_connection(client)
        return client

    def _test_connection(self, client: RecordListsApiClient) -> None:
        """Check if the created client can be used to perform a request.

        This method tests both that the API definition can be accessed and that the Granta MI
        version is compatible with this package.

        The first checks ensures that the Server API exists and is functional. The second check
        ensures that the Granta MI server version is compatible with this version of the package.

        A failure at any point raises a ConnectionError.

        Parameters
        ----------
        client : :class:`~.RecordListsApiClient`
            Client object to test.

        Raises
        ------
        ConnectionError
            Error raised if the connection test fails.
        """
        try:
            client.call_api(resource_path=API_DEFINITION_PATH, method="GET")
        except ApiException as e:
            self._process_api_exception(e)
        except requests.exceptions.RetryError as e:
            self._process_retry_error(e)

    @staticmethod
    def _process_api_exception(exception: ApiException) -> None:
        if exception.status_code == 404:
            raise ConnectionError(
                "Cannot find the Server API definition in Granta MI Service Layer. Ensure a "
                "compatible version of Granta MI is available try again."
            ) from exception
        else:
            raise ConnectionError(
                "An unexpected error occurred when trying to connect Server API in Granta MI "
                "Service Layer. Check the Service Layer logs for more information and try "
                "again."
            ) from exception

    @staticmethod
    def _process_retry_error(exception: requests.exceptions.RetryError) -> None:
        raise ConnectionError(
            "An unexpected error occurred when trying to connect Granta MI Server API. Check "
            "that SSL certificates have been configured for communications between Granta MI "
            "Server and client Granta MI applications."
        ) from exception
