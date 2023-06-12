from typing import List, Optional, Tuple, Union

from ansys.grantami.serverapi_openapi import api, models  # type: ignore[import]
from ansys.openapi.common import (  # type: ignore[import]
    ApiClient,
    ApiClientFactory,
    ApiException,
    SessionConfiguration,
    generate_user_agent,
)
import requests  # type: ignore[import]

from ._logger import logger
from ._models import BooleanCriterion, RecordList, RecordListItem, SearchCriterion, SearchResult

PROXY_PATH = "/proxy/v1.svc"
AUTH_PATH = "/Health/v2.svc"
API_DEFINITION_PATH = "/swagger/v1/swagger.json"
GRANTA_APPLICATION_NAME_HEADER = "PyGranta RecordLists"

MINIMUM_GRANTA_MI_VERSION = (23, 2)

_ArgNotProvided = "_ArgNotProvided"


def _get_mi_server_version(client: ApiClient) -> Tuple[int, ...]:
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
    schema_api = api.SchemaApi(client)
    server_version_response = schema_api.v1alpha_schema_mi_version_get()
    server_version_elements = server_version_response.version.split(".")
    server_version = tuple([int(e) for e in server_version_elements])
    return server_version


class RecordListsApiClient(ApiClient):  # type: ignore[misc]
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

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} url: {self._service_layer_url}>"

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
        record_lists = self.list_management_api.api_v1_lists_get()
        return [RecordList._from_model(record_list) for record_list in record_lists]

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
        record_list = self.list_management_api.api_v1_lists_list_list_identifier_get(identifier)
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
        response_options = models.GrantaServerApiListsDtoResponseOptions(
            include_record_list_items=include_items,
        )
        search_info = self.list_management_api.api_v1_lists_search_post(
            body=models.GrantaServerApiListsDtoRecordListSearchRequest(
                search_criterion=criterion._to_model(),
                response_options=response_options,
            )
        )

        search_results = (
            self.list_management_api.api_v1_lists_search_results_result_resource_identifier_get(
                search_info.search_result_identifier
            )
        )
        return [
            SearchResult._from_model(search_result, include_items)
            for search_result in search_results
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
        items = self.list_item_api.api_v1_lists_list_list_identifier_items_get(
            record_list.identifier
        )
        return [RecordListItem._from_model(item) for item in items.items]

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
        response_items = self.list_item_api.api_v1_lists_list_list_identifier_items_add_post(
            record_list.identifier,
            body=models.GrantaServerApiListsDtoRecordListItems(
                items=[item._to_model() for item in items]
            ),
        )
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
        response_items = self.list_item_api.api_v1_lists_list_list_identifier_items_remove_post(
            record_list.identifier,
            body=models.GrantaServerApiListsDtoRecordListItems(
                items=[item._to_model() for item in items]
            ),
        )
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
        if items is not None:
            items = models.GrantaServerApiListsDtoRecordListItems(
                items=[list_item._to_model() for list_item in items]
            )

        created_list = self.list_management_api.api_v1_lists_post(
            body=models.GrantaServerApiListsDtoRecordListCreate(
                name=name,
                description=description,
                notes=notes,
                items=items,
            ),
        )
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
        self.list_management_api.api_v1_lists_list_list_identifier_delete(record_list.identifier)

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

        body = []
        if name != _ArgNotProvided:
            body.append(self._create_patch_operation(name, "name"))
        if description != _ArgNotProvided:
            body.append(self._create_patch_operation(description, "description"))
        if notes != _ArgNotProvided:
            body.append(self._create_patch_operation(notes, "notes"))

        updated_resource = self.list_management_api.api_v1_lists_list_list_identifier_patch(
            record_list.identifier, body=body
        )
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
        list_copy = self.list_management_api.api_v1_lists_list_list_identifier_copy_post(
            record_list.identifier
        )
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
        list_revision = self.list_management_api.api_v1_lists_list_list_identifier_revise_post(
            record_list.identifier,
        )
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
        updated_list = (
            self.list_management_api.api_v1_lists_list_list_identifier_request_approval_post(
                record_list.identifier
            )
        )
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
        updated_list = self.list_management_api.api_v1_lists_list_list_identifier_publish_post(
            record_list.identifier,
        )
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
        updated_list = self.list_management_api.api_v1_lists_list_list_identifier_unpublish_post(
            record_list.identifier,
        )
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
        updated_list = self.list_management_api.api_v1_lists_list_list_identifier_reset_post(
            record_list.identifier,
        )
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
        self.list_permissions_api.api_v1_lists_list_list_identifier_permissions_subscribe_post(
            record_list.identifier
        )

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
        self.list_permissions_api.api_v1_lists_list_list_identifier_permissions_unsubscribe_post(
            record_list.identifier
        )

    @staticmethod
    def _create_patch_operation(
        value: Optional[str], name: str, op: str = "replace"
    ) -> models.JsonPatchDocument:
        return models.JsonPatchDocument(
            value=value,
            path=f"/{name}",
            op=op,
        )


class Connection(ApiClientFactory):  # type: ignore[misc]
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
        self._session_configuration.headers[
            "X-Granta-ApplicationName"
        ] = GRANTA_APPLICATION_NAME_HEADER
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
        client = RecordListsApiClient(
            self._session,
            self._base_service_layer_url,
            self._session_configuration,
        )
        client.setup_client(models)
        self._test_connection(client)
        return client

    @staticmethod
    def _test_connection(client: RecordListsApiClient) -> None:
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
            if e.status_code == 404:
                raise ConnectionError(
                    "Cannot find the Server API definition in Granta MI Service Layer. Ensure a "
                    "compatible version of Granta MI is available try again."
                ) from e
            else:
                raise ConnectionError(
                    "An unexpected error occurred when trying to connect Server API in Granta MI "
                    "Service Layer. Check the Service Layer logs for more information and try "
                    "again."
                ) from e
        except requests.exceptions.RetryError as e:
            raise ConnectionError(
                "An unexpected error occurred when trying to connect Granta MI Server API. Check "
                "that SSL certificates have been configured for communications between Granta MI "
                "Server and client Granta MI applications."
            ) from e

        try:
            server_version = _get_mi_server_version(client)
        except ApiException as e:
            raise ConnectionError(
                "Cannot check the Granta MI server version. Ensure the Granta MI server version "
                f"is at least {'.'.join([str(e) for e in MINIMUM_GRANTA_MI_VERSION])}."
            ) from e

        # Once there are multiple versions of this package targeting different Granta MI server
        # versions, the error message should direct users towards the PyGranta meta-package for
        # older versions. This is not necessary now though, because there is no support for
        # versions older than 2023 R2.

        if server_version < MINIMUM_GRANTA_MI_VERSION:
            raise ConnectionError(
                f"This package requires a more recent Granta MI version. Detected Granta MI server "
                f"version is {'.'.join([str(e) for e in server_version])}, but this package "
                f"requires at least {'.'.join([str(e) for e in MINIMUM_GRANTA_MI_VERSION])}."
            )
