from typing import List, Optional

import requests
from ansys.grantami.serverapi_openapi import api, models
from ansys.openapi.common import (
    ApiClient,
    SessionConfiguration,
    ApiClientFactory,
)

from ansys.grantami.recordlists.models import RecordList, RecordListItem
from ansys.grantami.recordlists._utils import _ArgNotProvided, extract_identifier


AUTH_PATH = "/swagger/v1/swagger.json"


class RecordListApiClient(ApiClient):
    """
    Communicates with Granta MI.

    This class is instantiated by the
    :class:`ansys.grantami.recordlists.ServerApiFactory` class and should not be instantiated
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
        Perform a request against the Server API to retrieve all defined Record Lists available for
        the user.
        """

        record_lists = self.list_management_api.api_v1_lists_get()
        return [RecordList.from_model(record_list) for record_list in record_lists]

    def get_list(self, identifier: str) -> RecordList:
        """
        Perform a request against the Server API to retrieve a Record List specified by its UUID
        identifier.
        """

        record_list = self.list_management_api.api_v1_lists_list_list_identifier_get(identifier)
        return RecordList.from_model(record_list)

    def get_list_items(self, identifier: str) -> List[RecordListItem]:
        """
        Perform a request against the Server API to retrieve all items included in a Record List
        specified by its UUID identifier.
        """

        items = self.list_item_api.api_v1_lists_list_list_identifier_items_get(identifier)
        return [RecordListItem.from_model(item) for item in items.items]

    def add_items_to_list(self, identifier: str, items: List[RecordListItem]):
        """
        Perform a request against the Server API to add items to the Record List
        specified by its UUID identifier.
        """

        if not items:
            return

        self.list_item_api.api_v1_lists_list_list_identifier_items_add_post(
            identifier,
            body=models.GrantaServerApiListsDtoRecordListItems(
                items=[item.to_model() for item in items]
            ),
        )

    def remove_items_from_list(self, identifier: str, items: List[RecordListItem]):
        """
        Perform a request against the Server API to remove items from the Record List
        specified by its UUID identifier.
        """

        if not items:
            return

        self.list_item_api.api_v1_lists_list_list_identifier_items_remove_post(
            identifier,
            body=models.GrantaServerApiListsDtoRecordListItems(
                items=[item.to_model() for item in items]
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
        Create a new list and push it to Server API. The identifier of the created RecordList is
        returned.
        """
        if items is not None:
            items = models.GrantaServerApiListsDtoRecordListItems(
                items=[list_item.to_model() for list_item in items]
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
        Perform a request against the Server API to delete a Record List specified by its UUID
        identifier.
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
        Perform a request against the Server API to update a RecordList specified by its UUID
        identifier with the properties provided, and returns the updated RecordList.
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
        return RecordList.from_model(updated_resource)

    def copy_list(self, identifier: str) -> str:
        """
        Perform a request against the Server API to copy a Record List specified by its UUID
        identifier.
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
        Perform a request against the Server API to revise a Record List specified by its UUID
        identifier.

        # TODO: revising requires a published list, otherwise 403 forbidden
        # TODO Explain what revising a list is about
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


class Connection(ApiClientFactory):
    """
    Connects to a Granta MI ServerAPI instance.
    """

    def __init__(self, api_url: str, session_configuration: Optional[SessionConfiguration] = None):
        auth_url = api_url.strip("/") + AUTH_PATH
        super().__init__(auth_url, session_configuration)
        self._base_server_api_url = api_url

    def connect(self) -> RecordListApiClient:
        """
        Finalize the RecordList client and return it for use.

        Authentication must be configured for this method to succeed.
        """
        self._validate_builder()
        client = RecordListApiClient(
            self._session,
            self._base_server_api_url,
            self._session_configuration,
        )
        client.setup_client(models)
        # TODO: test connection
        return client
