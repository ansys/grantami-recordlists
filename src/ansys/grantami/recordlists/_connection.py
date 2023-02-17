from typing import Dict, List, Optional

import requests
from ansys.grantami.serverapi_openapi import api, models
from ansys.openapi.common import (
    ApiClient,
    SessionConfiguration,
    ApiClientFactory,
)

from ansys.grantami.recordlists.models import RecordList, RecordListItem


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
        return [RecordList.from_model(self, record_list) for record_list in record_lists]

    def get_list(self, identifier: str) -> RecordList:
        """
        Perform a request against the Server API to retrieve a Record List specified by its UUID
        identifier.
        """

        return RecordList.from_model(self, self._get_list(identifier))

    def _get_list(self, identifier: str) -> models.GrantaServerApiListsDtoRecordListHeader:
        return self.list_management_api.api_v1_lists_list_list_identifier_get(identifier)

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
    ) -> RecordList:
        """Create a new list and push it to Server API. The created RecordList is returned."""
        identifier = self._create_list(name, description, notes, items)
        return self.get_list(identifier)

    def _create_list(
        self,
        name: str,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        items: Optional[List[RecordListItem]] = None,
    ) -> str:
        """Perform a request against the Server API to create a new Record List."""
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
            return response.resource_uri.split("/")[-1]
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
        **kwargs: Dict[str, Optional[str]],
    ) -> None:
        """
        Perform a request against the Server API to update a Record List specified by its UUID
        identifier, with the properties provided.
        # TODO document kwargs
        """
        _nullable = ["notes", "description"]
        _non_nullable = ["name"]
        _all_properties = _non_nullable + _nullable

        if not kwargs:
            raise ValueError(
                f"Update must include at least one property to update. "
                f"Supported properties are {_all_properties}"
            )

        unexpected_args = [key for key in kwargs.keys() if key not in _all_properties]
        if unexpected_args:
            raise ValueError(
                f"Properties {unexpected_args} are not supported for update. Supported properties"
                f" are {_all_properties}"
            )

        unexpected_none_args = [
            name for name, value in kwargs.items() if name not in _nullable and value is None
        ]
        if unexpected_none_args:
            raise ValueError(
                f"Properties {unexpected_none_args} cannot be None. "
                f"The following properties are nullable {_nullable}"
            )

        body = []
        for name, value in kwargs.items():
            operation = models.MicrosoftAspNetCoreJsonPatchOperationsOperation(
                value=value,
                path=f"/{name}",
                op="replace",
            )
            body.append(operation)

        self.list_management_api.api_v1_lists_list_list_identifier_patch(identifier, body=body)


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
