from typing import List

import requests
from ansys.grantami.serverapi_openapi import api, models
from ansys.openapi.common import ApiClient, SessionConfiguration, ApiClientFactory, ApiConnectionException

from ansys.grantami.recordlists.models import RecordListHeader, RecordListItem


class RecordListApiClient(ApiClient):

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
        return [RecordListHeader.from_model(l) for l in self.list_management_api.api_v1_lists_get()]

    def get_list(self, identifier: str) -> RecordListHeader:
        return RecordListHeader.from_model(self.list_management_api.api_v1_lists_list_list_identifier_get(identifier))

    def get_list_items(self, identifier: str) -> List[RecordListItem]:
        items = self.list_item_api.api_v1_lists_list_list_identifier_items_get(identifier)
        return [RecordListItem.from_model(item) for item in items.items]


class ServerApiFactory(ApiClientFactory):
    def _ApiClientFactory__test_connection(self):
        test_path = "/swagger/v1/swagger.json"
        resp = self._session.get(self._api_url + test_path)
        if 200 <= resp.status_code < 300:
            return True
        else:
            raise ApiConnectionException(resp.status_code, resp.reason, resp.text)

    def connect(self) -> RecordListApiClient:
        self._validate_builder()
        client = RecordListApiClient(self._session, self._api_url, self._session_configuration)
        client.setup_client(models)
        return client
