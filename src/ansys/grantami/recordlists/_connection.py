from typing import List, Optional

from ansys.grantami.serverapi_openapi import api, models
from ansys.openapi.common import ApiClient, ApiClientFactory, SessionConfiguration
import requests

from ansys.grantami.recordlists._utils import _ArgNotProvided, extract_identifier
from ansys.grantami.recordlists.models import RecordList, RecordListItem

PROXY_PATH = "/proxy/v1.svc"
AUTH_PATH = "/Health/v2.svc"


class RecordListApiClient(ApiClient):
    """
    Communicates with Granta MI.

    This class is instantiated by the
    :class:`~ansys.grantami.recordlists.Connection` class and should not be instantiated
    directly.
    """

    def __init__(
        self,
        session: requests.Session,
        api_url: str,
        configuration: SessionConfiguration,
    ):
        super().__init__(session, api_url, configuration)
        self.list_management_api = api.ListManagementApi(self)
        self.list_item_api = api.ListItemApi(self)
        self.list_permissions_api = api.ListPermissionsApi(self)

    def get_all_lists(self) -> List[RecordList]:
        """
        Get the details of all record lists available for the current user.

        Performs an HTTP request against the Server API.
        """
        record_lists = self.list_management_api.api_v1_lists_get()
        return [RecordList._from_model(record_list) for record_list in record_lists]

    def get_list(self, identifier: str) -> RecordList:
        """
        Get the details of a record list.

        Performs an HTTP request against the Server API.

        Parameters
        ----------
        identifier :
            Unique identifier of the record list.
        """
        record_list = self.list_management_api.api_v1_lists_list_list_identifier_get(identifier)
        return RecordList._from_model(record_list)

    def get_list_items(self, identifier: str) -> List[RecordListItem]:
        """
        Get all items included in a record list.

        Performs an HTTP request against the Server API.

        Parameters
        ----------
        identifier :
            Unique identifier of the record list.
        """
        items = self.list_item_api.api_v1_lists_list_list_identifier_items_get(identifier)
        return [RecordListItem._from_model(item) for item in items.items]

    def add_items_to_list(self, identifier: str, items: List[RecordListItem]):
        """
        Add items to a record list.

        Performs an HTTP request against the Server API.
        Items are not validated against existing records on the server or existing items in the
        list.

        Parameters
        ----------
        identifier :
            Unique identifier of the record list.
        items:
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

    def remove_items_from_list(self, identifier: str, items: List[RecordListItem]):
        """
        Remove items from a record list.

        Performs an HTTP request against the Server API.
        Attempting to remove items that are not in the list will not result in an error.

        Parameters
        ----------
        identifier :
            Unique identifier of the record list.
        items:
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
        name :
            Name of the record list.
        description :
            Description of the record list.
        notes :
            Notes of the record list.
        items :
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
        if status_code == 201:
            response = self.deserialize(response, "GrantaServerApiListsDtoRecordListResource")
            response: models.GrantaServerApiListsDtoRecordListResource
            return extract_identifier(response)
        else:
            return None

    def delete_list(self, identifier: str) -> None:
        """
        Delete a record list.

        Performs an HTTP request against the Server API.

        Parameters
        ----------
        identifier :
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_delete(identifier)

    def update_list(
        self,
        identifier: str,
        name: str = _ArgNotProvided,
        description: Optional[str] = _ArgNotProvided,
        notes: Optional[str] = _ArgNotProvided,
    ) -> RecordList:
        """
        Update a record list with the provided arguments.

        Performs an HTTP request against the Server API.

        Parameters
        ----------
        identifier :
            Unique identifier of the record list.
        name :
            New value for the name of the record list.
        description :
            New value for the description of the record list.
        notes :
            New value for the notes of the record list.

        Returns
        -------
        RecordList
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
        identifier :
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
        if status_code == 201:
            response = self.deserialize(response, "GrantaServerApiListsDtoRecordListResource")
            response: models.GrantaServerApiListsDtoRecordListResource
            return extract_identifier(response)
        else:
            return None

    def revise_list(self, identifier: str) -> str:
        """
        Revise a record list.

        Performs an HTTP request against the Server API.
        Revising a list allows a user to create a personal copy of a published list and to modify
        its items or details. When the 'in-revision' list is published, it overwrites the original
        list.

        Parameters
        ----------
        identifier :
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
        if status_code == 201:
            response = self.deserialize(response, "GrantaServerApiListsDtoRecordListResource")
            response: models.GrantaServerApiListsDtoRecordListResource
            return extract_identifier(response)
        else:
            # TODO returning None isn't helpful at all. Consider raising an Exception instead with
            #  the content of the response, should it include any information about what happened
            #  server-side (same for all three methods using this workaround)
            return None

    @staticmethod
    def _create_patch_operation(
        value: Optional[str], name: str, op="replace"
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
        identifier :
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
        list, use :meth:`Record.revise_list`.

        Parameters
        ----------
        identifier :
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_publish_post(identifier)

    def unpublish(self, identifier: str) -> None:
        """
        Withdraw a record list.

        Performs an HTTP request against the Server API.
        The list must be published and awaiting approval. Withdrawing the list updates
        the "published" status to False and resets the awaiting approval status.
        # TODO who has still access to the list? Original author?
        All existing subscriptions will be lost on withdrawal.

        Parameters
        ----------
        identifier :
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
        identifier :
            Unique identifier of the record list.
        """
        self.list_management_api.api_v1_lists_list_list_identifier_reset_post(identifier)


class Connection(ApiClientFactory):
    """Connects to a Granta MI ServerAPI instance."""

    def __init__(
        self, servicelayer_url: str, session_configuration: Optional[SessionConfiguration] = None
    ):
        auth_url = servicelayer_url.strip("/") + AUTH_PATH
        super().__init__(auth_url, session_configuration)
        self._base_service_layer_url = servicelayer_url

    def connect(self) -> RecordListApiClient:
        """
        Finalize the RecordList client and return it for use.

        Authentication must be configured for this method to succeed.
        """
        self._validate_builder()
        client = RecordListApiClient(
            self._session,
            self._base_service_layer_url + PROXY_PATH,
            self._session_configuration,
        )
        client.setup_client(models)
        # TODO: test connection
        return client
