from typing import List

import requests
from ansys.grantami.serverapi_openapi import api, models
from ansys.openapi.common import (
    ApiClient,
    SessionConfiguration,
    ApiClientFactory,
    ApiConnectionException,
)

from ansys.grantami.recordlists.models import RecordListHeader, RecordListItem


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

    def get_all_lists(self) -> List[RecordListHeader]:
        """
        Perform a request against the Server API to retrieve all defined Record Lists available for
        the user.
        """

        return [RecordListHeader.from_model(l) for l in self.list_management_api.api_v1_lists_get()]

    def get_list(self, identifier: str) -> RecordListHeader:
        """
        Perform a request against the Server API to retrieve a Record List specified by its UUID
        identifier.
        """

        return RecordListHeader.from_model(
            self.list_management_api.api_v1_lists_list_list_identifier_get(identifier)
        )

    def get_list_items(self, identifier: str) -> List[RecordListItem]:
        """
        Perform a request against the Server API to retrieve all items included in a Record List
        specified by its UUID identifier.
        """

        items = self.list_item_api.api_v1_lists_list_list_identifier_items_get(identifier)
        return [RecordListItem.from_model(item) for item in items.items]


class ServerApiFactory(ApiClientFactory):
    """
    Connects to a Granta MI ServerAPI instance.
    """

    def _ApiClientFactory__test_connection(self):
        test_path = "/swagger/v1/swagger.json"
        resp = self._session.get(self._api_url + test_path)
        if 200 <= resp.status_code < 300:
            return True
        else:
            raise ApiConnectionException(resp.status_code, resp.reason, resp.text)

    def connect(self) -> RecordListApiClient:
        """
        Finalize the RecordList client and return it for use.

        Authentication must be configured for this method to succeed.
        """
        self._validate_builder()
        client = RecordListApiClient(self._session, self._api_url, self._session_configuration)
        client.setup_client(models)
        return client
