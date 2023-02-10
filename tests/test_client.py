from typing import Type, Any
from unittest.mock import Mock

import pytest

from ansys.grantami.recordlists._connection import RecordListApiClient
from ansys.grantami.recordlists.models import RecordListItem
from ansys.grantami.serverapi_openapi.api import ListManagementApi, ListItemApi
from ansys.grantami.serverapi_openapi.models import (
    GrantaServerApiListsDtoRecordListHeader,
    GrantaServerApiListsDtoRecordListItems,
    GrantaServerApiListsDtoListItem,
)


@pytest.fixture
def client():
    client = RecordListApiClient(Mock(), Mock(), Mock())
    return client


class TestClientMethod:
    _return_value: Any
    _api: Type
    _api_method: str

    @pytest.fixture
    def api_method(self, monkeypatch):
        mocked_method = Mock(return_value=self._return_value)
        monkeypatch.setattr(self._api, self._api_method, mocked_method)
        return mocked_method


class TestReadList(TestClientMethod):
    _return_value = Mock(spec=GrantaServerApiListsDtoRecordListHeader)
    _api = ListManagementApi
    _api_method = "api_v1_lists_list_list_identifier_get"

    def test_read_list(self, client, api_method):
        identifier = "00000-0000a"
        client.get_list(identifier)
        api_method.assert_called_once_with(identifier)

    # TODO test variations of invalid identifiers


class TestReadAllLists(TestClientMethod):
    _return_value = []
    _api = ListManagementApi
    _api_method = "api_v1_lists_get"

    def test_read_all_lists(self, client, api_method):
        lists = client.get_all_lists()
        api_method.assert_called_once_with()
        assert lists == []

    # TODO test with return value


class TestReadItems(TestClientMethod):
    r_value = Mock(spec=GrantaServerApiListsDtoRecordListItems)
    r_value.items = []
    _return_value = r_value
    _api = ListItemApi
    _api_method = "api_v1_lists_list_list_identifier_items_get"

    def test_read_items(self, client, api_method):
        identifier = "00000-0000a"
        items = client.get_list_items(identifier)

        api_method.assert_called_once_with(identifier)
        assert items == []

    # TODO test with return value


class TestAddItems(TestClientMethod):
    _return_value = None
    _api = ListItemApi
    _api_method = "api_v1_lists_list_list_identifier_items_add_post"

    @pytest.mark.parametrize("items", [None, [], set()])
    def test_add_no_items(self, client, api_method, items):
        identifier = "00000-0000a"
        response = client.add_items_to_list(identifier, items)

        assert response is None
        api_method.assert_not_called()

    def test_add_items(self, client, api_method):
        identifier = "00000-0000a"
        items = [RecordListItem("a", "b", "c")]
        expected_body = GrantaServerApiListsDtoRecordListItems(
            items=[
                GrantaServerApiListsDtoListItem(
                    database_guid="a",
                    table_guid="b",
                    record_history_guid="c",
                )
            ]
        )

        response = client.add_items_to_list(identifier, items)

        assert response is None
        api_method.assert_called_once_with(identifier, body=expected_body)


class TestRemoveItems(TestClientMethod):
    _return_value = None
    _api = ListItemApi
    _api_method = "api_v1_lists_list_list_identifier_items_remove_post"

    @pytest.mark.parametrize("items", [None, [], set()])
    def test_remove_no_items(self, client, api_method, items):
        identifier = "00000-0000a"
        response = client.remove_items_from_list(identifier, items)

        assert response is None
        api_method.assert_not_called()

    def test_add_items(self, client, api_method):
        identifier = "00000-0000a"
        items = [RecordListItem("a", "b", "c")]
        expected_body = GrantaServerApiListsDtoRecordListItems(
            items=[
                GrantaServerApiListsDtoListItem(
                    database_guid="a",
                    table_guid="b",
                    record_history_guid="c",
                )
            ]
        )

        response = client.remove_items_from_list(identifier, items)

        assert response is None
        api_method.assert_called_once_with(identifier, body=expected_body)
