from typing import List, Optional, Union

from ansys.grantami.serverapi_openapi import api, models  # type: ignore[import]
from ansys.openapi.common import (  # type: ignore[import]
    ApiClient,
    ApiClientFactory,
    ApiException,
    SessionConfiguration,
)
import requests  # type: ignore[import]

from ._models import BooleanCriterion, RecordList, RecordListItem, SearchCriterion, SearchResult

PROXY_PATH = "/proxy/v1.svc"
AUTH_PATH = "/Health/v2.svc"
API_DEFINITION_PATH = "/swagger/v1/swagger.json"

_ArgNotProvided = "_ArgNotProvided"


class RecordListApiClient(ApiClient):  # type: ignore[misc]
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

    def get_list_items(self, identifier: str) -> List[RecordListItem]:
        """
        Get all items included in a record list.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        list of :class:`.RecordListItem`
            List of items included in the record list.
        """
        items = self.list_item_api.api_v1_lists_list_list_identifier_items_get(identifier)
        return [RecordListItem._from_model(item) for item in items.items]

    def add_items_to_list(
        self, identifier: str, items: List[RecordListItem]
    ) -> List[RecordListItem]:
        """
        Add items to a record list.

        Performs an HTTP request against the Granta MI Server API.
        Items are not validated against existing records on the server or existing items in the
        list.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        items : list of :class:`.RecordListItem`
            List of items to add to the record list.

        Returns
        -------
        list of :class:`.RecordListItem`
           List of items included in the record list.
        """
        response_items = self.list_item_api.api_v1_lists_list_list_identifier_items_add_post(
            identifier,
            body=models.GrantaServerApiListsDtoRecordListItems(
                items=[item._to_model() for item in items]
            ),
        )
        return [RecordListItem._from_model(item) for item in response_items.items]

    def remove_items_from_list(
        self, identifier: str, items: List[RecordListItem]
    ) -> List[RecordListItem]:
        """
        Remove items from a record list.

        Performs an HTTP request against the Granta MI Server API.
        Attempting to remove items that are not in the list will not result in an error.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        items : list of :class:`.RecordListItem`
            List of items to remove from the record list.

        Returns
        -------
        list of :class:`.RecordListItem`
           List of items included in the record list.
        """
        response_items = self.list_item_api.api_v1_lists_list_list_identifier_items_remove_post(
            identifier,
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

    def delete_list(self, identifier: str) -> None:
        """
        Delete a record list.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_delete(identifier)

    def update_list(
        self,
        identifier: str,
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
        identifier : str
            Unique identifier of the record list.
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
            identifier, body=body
        )
        return RecordList._from_model(updated_resource)

    def copy_list(self, identifier: str) -> RecordList:
        """
        Create a copy of a record list.

        Performs an HTTP request against the Granta MI Server API.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        :class:`.RecordList`
            Copied record list details.
        """
        list_copy = self.list_management_api.api_v1_lists_list_list_identifier_copy_post(identifier)
        return RecordList._from_model(list_copy)

    def revise_list(self, identifier: str) -> RecordList:
        """
        Revise a record list.

        Performs an HTTP request against the Granta MI Server API.
        Revising a list allows a user to create a personal copy of a published list and to modify
        its items or details. When the 'in-revision' list is published, it overwrites the original
        list.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        :class:`.RecordList`
            Revision record list details.
        """
        list_revision = self.list_management_api.api_v1_lists_list_list_identifier_revise_post(
            identifier,
        )
        return RecordList._from_model(list_revision)

    def request_list_approval(self, identifier: str) -> RecordList:
        """
        Request approval for a record list.

        Performs an HTTP request against the Granta MI Server API.
        Requesting approval updates the ``awaiting approval`` status of the record list to ``True``.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        :class:`.RecordList`
            Updated record list details.
        """
        updated_list = (
            self.list_management_api.api_v1_lists_list_list_identifier_request_approval_post(
                identifier
            )
        )
        return RecordList._from_model(updated_list)

    def publish_list(self, identifier: str) -> RecordList:
        """
        Publish a record list.

        Performs an HTTP request against the Granta MI Server API.
        The list must be awaiting approval and not published already. Publishing the list updates
        the status to *published* and resets the awaiting approval status.
        Published lists can be viewed by all users and cannot be modified. To modify a published
        list, use :meth:`.revise_list`.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        :class:`.RecordList`
            Updated record list details.
        """
        updated_list = self.list_management_api.api_v1_lists_list_list_identifier_publish_post(
            identifier,
        )
        return RecordList._from_model(updated_list)

    def unpublish_list(self, identifier: str) -> RecordList:
        """
        Withdraw a record list.

        Performs an HTTP request against the Granta MI Server API.
        The list must be published and awaiting approval. Withdrawing the list updates
        the *published* status to False and resets the awaiting approval status.
        All existing subscriptions will be lost on withdrawal.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        :class:`.RecordList`
            Updated record list details.
        """
        updated_list = self.list_management_api.api_v1_lists_list_list_identifier_unpublish_post(
            identifier,
        )
        return RecordList._from_model(updated_list)

    def cancel_list_approval_request(self, identifier: str) -> RecordList:
        """
        Cancel a pending request for approval on a record list.

        Performs an HTTP request against the Granta MI Server API.
        The list must be awaiting approval. Cancelling the approval request resets the awaiting
        approval status to False.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        :class:`.RecordList`
            Updated record list details.
        """
        updated_list = self.list_management_api.api_v1_lists_list_list_identifier_reset_post(
            identifier,
        )
        return RecordList._from_model(updated_list)

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
    <RecordListApiClient: url=http://my_mi_server/mi_servicelayer>
    >>> client = (
    ...     Connection("http://my_mi_server/mi_servicelayer")
    ...     .with_credentials(username="my_username", password="my_password")
    ...     .connect()
    ... )
    >>> client
    <RecordListApiClient: url: http://my_mi_server/mi_servicelayer>
    """

    def __init__(
        self, servicelayer_url: str, session_configuration: Optional[SessionConfiguration] = None
    ):
        auth_url = servicelayer_url.strip("/") + AUTH_PATH
        super().__init__(auth_url, session_configuration)
        self._base_service_layer_url = servicelayer_url

    def connect(self) -> RecordListApiClient:
        """
        Finalize the :class:`.RecordListApiClient` client and return it for use.

        Authentication must be configured for this method to succeed.

        Returns
        -------
        :class:`.RecordListApiClient`
            Client object that can be used to connect to Granta MI and interact with the record
            list API.
        """
        self._validate_builder()
        client = RecordListApiClient(
            self._session,
            self._base_service_layer_url,
            self._session_configuration,
        )
        client.setup_client(models)
        self._test_connection(client)
        return client

    @staticmethod
    def _test_connection(client: RecordListApiClient) -> None:
        """Check if the created client can be used to perform a request.

        This method asserts that the API definition can be obtained.
        It specifically checks for a 404 error, which most likely means that the targeted Service
        Layer does not include Server API.

        Parameters
        ----------
        client : :class:`~.RecordListApiClient`
            Client object to test.

        Raises
        ------
        ConnectionError
            Error raised if the test query fails.
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
