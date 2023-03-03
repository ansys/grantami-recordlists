from typing import List, Optional, Union, cast

from ansys.grantami.serverapi_openapi import api, models  # type: ignore[import]
from ansys.openapi.common import (  # type: ignore[import]
    ApiClient,
    ApiClientFactory,
    SessionConfiguration,
)
import requests  # type: ignore[import]

from ._utils import _ArgNotProvided, extract_identifier
from .models import BooleanCriterion, RecordList, RecordListItem, SearchCriterion, SearchResult

PROXY_PATH = "/proxy/v1.svc"
AUTH_PATH = "/Health/v2.svc"


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

        Performs an HTTP request against the Server API.

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

        Performs an HTTP request against the Server API.

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

    def search(
        self,
        criterion: Union[BooleanCriterion, SearchCriterion],
        include_items: bool = False,
        include_permissions: bool = False,
        include_actions: bool = False,
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
        include_permissions: bool
            Whether the search results should include the current user's permissions on the
            associated list.
        include_actions: bool
            Whether the search results should include the current user's possible actions on the
            associated list.

        Returns
        -------
        list of :class:`.SearchResult`
            List of record lists matching the provided criterion.
        """
        response_options = models.GrantaServerApiListsDtoResponseOptions(
            include_record_list_items=include_items,
            include_user_permissions=include_permissions,
            include_user_actions=include_actions,
        )
        search_resource = self.list_management_api.api_v1_lists_search_post(
            body=models.GrantaServerApiListsDtoRecordListSearchRequest(
                search_criterion=criterion._to_model(),
                response_options=response_options,
            )
        )

        search_resource_identifier = extract_identifier(search_resource)
        search_results = (
            self.list_management_api.api_v1_lists_search_results_result_resource_identifier_get(
                search_resource_identifier
            )
        )
        return [
            SearchResult._from_model(
                search_result, include_items, include_permissions, include_actions
            )
            for search_result in search_results
        ]

    def get_list_items(self, identifier: str) -> List[RecordListItem]:
        """
        Get all items included in a record list.

        Performs an HTTP request against the Server API.

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

    def add_items_to_list(self, identifier: str, items: List[RecordListItem]) -> None:
        """
        Add items to a record list.

        Performs an HTTP request against the Server API.
        Items are not validated against existing records on the server or existing items in the
        list.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        items : list of :class:`.RecordListItem`
            List of items to add to the record list.
        """
        if not items:
            return

        self.list_item_api.api_v1_lists_list_list_identifier_items_add_post(
            identifier,
            body=models.GrantaServerApiListsDtoRecordListItems(
                items=[item._to_model() for item in items]
            ),
        )

    def remove_items_from_list(self, identifier: str, items: List[RecordListItem]) -> None:
        """
        Remove items from a record list.

        Performs an HTTP request against the Server API.
        Attempting to remove items that are not in the list will not result in an error.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        items : list of :class:`.RecordListItem`
            List of items to remove from the record list.
        """
        if not items:
            return

        self.list_item_api.api_v1_lists_list_list_identifier_items_remove_post(
            identifier,
            body=models.GrantaServerApiListsDtoRecordListItems(
                items=[item._to_model() for item in items]
            ),
        )

    def create_list(
        self,
        name: str,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        items: Optional[List[RecordListItem]] = None,
    ) -> str:
        """
        Create a new record list with the provided arguments.

        Performs an HTTP request against the Server API.

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
        str
            Unique identifier of the created record list.
        """
        if items is not None:
            items = models.GrantaServerApiListsDtoRecordListItems(
                items=[list_item._to_model() for list_item in items]
            )

        # TODO Workaround until Server API documents 201 response
        response, status_code, _ = self.list_management_api.api_v1_lists_post_with_http_info(
            _preload_content=False,
            body=models.GrantaServerApiListsDtoRecordListCreate(
                name=name,
                description=description,
                notes=notes,
                items=items,
            ),
        )
        if status_code != 201:
            raise NotImplementedError("Expected response with status code 201")

        data = cast(
            models.GrantaServerApiListsDtoRecordListResource,
            self.deserialize(response, "GrantaServerApiListsDtoRecordListResource"),
        )
        return extract_identifier(data)

    def delete_list(self, identifier: str) -> None:
        """
        Delete a record list.

        Performs an HTTP request against the Server API.

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

        Performs an HTTP request against the Server API.

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

    def copy_list(self, identifier: str) -> str:
        """
        Create a copy of a record list.

        Performs an HTTP request against the Server API.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        str
            Unique identifier of the created record list.
        """
        # TODO remove temp workaround when API documents operation return type
        (
            response,
            status_code,
            _,
        ) = self.list_management_api.api_v1_lists_list_list_identifier_copy_post_with_http_info(
            identifier,
            _preload_content=False,
        )
        if status_code != 201:
            raise NotImplementedError("Expected response with status code 201")

        data = cast(
            models.GrantaServerApiListsDtoRecordListResource,
            self.deserialize(response, "GrantaServerApiListsDtoRecordListResource"),
        )
        return extract_identifier(data)

    def revise_list(self, identifier: str) -> str:
        """
        Revise a record list.

        Performs an HTTP request against the Server API.
        Revising a list allows a user to create a personal copy of a published list and to modify
        its items or details. When the 'in-revision' list is published, it overwrites the original
        list.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.

        Returns
        -------
        str
            Unique identifier of the created personal record list.
        """
        # TODO remove temp workaround when API documents operation return type
        (
            response,
            status_code,
            _,
        ) = self.list_management_api.api_v1_lists_list_list_identifier_revise_post_with_http_info(
            identifier, _preload_content=False
        )
        if status_code != 201:
            raise NotImplementedError("Expected response with status code 201")

        data = cast(
            models.GrantaServerApiListsDtoRecordListResource,
            self.deserialize(response, "GrantaServerApiListsDtoRecordListResource"),
        )
        return extract_identifier(data)

    @staticmethod
    def _create_patch_operation(
        value: Optional[str], name: str, op: str = "replace"
    ) -> models.MicrosoftAspNetCoreJsonPatchOperationsOperation:
        return models.MicrosoftAspNetCoreJsonPatchOperationsOperation(
            value=value,
            path=f"/{name}",
            op=op,
        )

    def request_approval(self, identifier: str) -> None:
        """
        Request approval for a record list.

        Performs an HTTP request against the Server API.
        Requesting approval updates the ``awaiting approval`` status of the record list to `True`.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_request_approval_post(identifier)

    def publish(self, identifier: str) -> None:
        """
        Publish a record list.

        Performs an HTTP request against the Server API.
        The list must be awaiting approval and not published already. Publishing the list updates
        the status to "published" and resets the awaiting approval status.
        Published lists can be viewed by all users and cannot be modified. To modify a published
        list, use :meth:`.revise_list`.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_publish_post(identifier)

    def unpublish(self, identifier: str) -> None:
        """
        Withdraw a record list.

        Performs an HTTP request against the Server API.
        The list must be published and awaiting approval. Withdrawing the list updates
        the "published" status to False and resets the awaiting approval status.
        All existing subscriptions will be lost on withdrawal.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_unpublish_post(identifier)

    def reset_approval_request(self, identifier: str) -> None:
        """
        Cancel a pending request for approval on a record list.

        Performs an HTTP request against the Server API.
        The list must be awaiting approval. Cancelling the approval request resets the awaiting
        approval status to False.

        Parameters
        ----------
        identifier : str
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_reset_post(identifier)


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
        # TODO: test connection
        return client
