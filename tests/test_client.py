import uuid
from typing import Type, Any
from unittest.mock import Mock

import pytest
import requests

from ansys.grantami.recordlists._connection import RecordListApiClient
from ansys.grantami.recordlists.models import RecordListItem
from ansys.grantami.serverapi_openapi.api import ListManagementApi, ListItemApi
from ansys.grantami.serverapi_openapi import models
from ansys.grantami.serverapi_openapi.models import (
    GrantaServerApiListsDtoRecordListHeader,
    GrantaServerApiListsDtoRecordListItems,
    GrantaServerApiListsDtoListItem,
    MicrosoftAspNetCoreJsonPatchOperationsOperation,
    GrantaServerApiListsDtoRecordListResource,
    GrantaServerApiListsDtoRecordListCreate,
)


@pytest.fixture
def client():
    client = RecordListApiClient(Mock(), Mock(), Mock())
    client.setup_client(models)
    return client


class TestClientMethod:
    _return_value: Any
    _api: Type
    _api_method: str
    _mock_uuid = str(uuid.uuid4())

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


# TODO unit test for create list when server-openapi documents its 201 response.


class TestDeleteList(TestClientMethod):
    _return_value = None
    _api = ListManagementApi
    _api_method = "api_v1_lists_list_list_identifier_delete"

    def test_delete_list(self, client, api_method):
        identifier = "00000-0000a"
        client.delete_list(identifier)
        api_method.assert_called_once_with(identifier)


class TestUpdate(TestClientMethod):
    _return_value = Mock(spec=GrantaServerApiListsDtoRecordListHeader)
    _api = ListManagementApi
    _api_method = "api_v1_lists_list_list_identifier_patch"

    def test_update_list_no_args(self, client, api_method):
        with pytest.raises(ValueError, match="at least one property"):
            client.update_list(self._mock_uuid)
        api_method.assert_not_called()

    def test_update_list_single_non_nullable_args(self, client, api_method):
        with pytest.raises(ValueError):
            client.update_list(self._mock_uuid, name=None)
        api_method.assert_not_called()

    @pytest.mark.parametrize("prop_name", ["notes", "description"])
    def test_update_list_single_nullable_args(self, client, api_method, prop_name):
        client.update_list(self._mock_uuid, **{prop_name: None})
        expected_body = [
            MicrosoftAspNetCoreJsonPatchOperationsOperation(
                value=None,
                path=f"/{prop_name}",
                op="replace",
            )
        ]
        api_method.assert_called_once_with(self._mock_uuid, body=expected_body)


class TestPublishList(TestClientMethod):
    _return_value = Mock(spec=GrantaServerApiListsDtoRecordListResource, resource_uri=uuid.uuid4())
    _api = ListManagementApi
    _api_method = "api_v1_lists_list_list_identifier_publish_post"

    def test_publish_list(self, client, api_method):
        identifier = "00000-0000a"
        client.publish(identifier)
        api_method.assert_called_once_with(identifier)


class TestUnpublishList(TestClientMethod):
    _return_value = Mock(spec=GrantaServerApiListsDtoRecordListResource, resource_uri=uuid.uuid4())
    _api = ListManagementApi
    _api_method = "api_v1_lists_list_list_identifier_unpublish_post"

    def test_unpublish_list(self, client, api_method):
        identifier = "00000-0000a"
        client.unpublish(identifier)
        api_method.assert_called_once_with(identifier)


class TestResetApprovalList(TestClientMethod):
    _return_value = Mock(spec=GrantaServerApiListsDtoRecordListResource, resource_uri=uuid.uuid4())
    _api = ListManagementApi
    _api_method = "api_v1_lists_list_list_identifier_reset_post"

    def test_reset_approval(self, client, api_method):
        identifier = "00000-0000a"
        client.reset_approval_request(identifier)
        api_method.assert_called_once_with(identifier)


class TestRequestApprovalList(TestClientMethod):
    _return_value = Mock(spec=GrantaServerApiListsDtoRecordListResource, resource_uri=uuid.uuid4())
    _api = ListManagementApi
    _api_method = "api_v1_lists_list_list_identifier_request_approval_post"

    def test_request_approval(self, client, api_method):
        identifier = "00000-0000a"
        client.request_approval(identifier)
        api_method.assert_called_once_with(identifier)


@pytest.fixture
def mock_id():
    return str(uuid.uuid4())


@pytest.fixture
def mock_api_method(request, monkeypatch, mock_id):
    method_name = getattr(request, "param", {}).get("method_name")
    mock = Mock(
        spec=requests.Response,
        status_code=201,
    )
    mock.json = Mock(
        return_value={
            "resourceUri": f"http://my_server_name/mi_servicelayer/proxy/v1.svc"
            f"/api/v1/lists/list/{mock_id}"
        }
    )

    mocked_method = Mock(return_value=(mock, 201, {}))
    monkeypatch.setattr(ListManagementApi, method_name, mocked_method)
    return mocked_method


@pytest.mark.parametrize(
    "mock_api_method", [{"method_name": "api_v1_lists_post_with_http_info"}], indirect=True
)
def test_create_list(client, mock_api_method, mock_id):
    list_name = "ListName"

    returned_identifier = client.create_list(list_name)

    expected_body = GrantaServerApiListsDtoRecordListCreate(name=list_name)
    mock_api_method.assert_called_once_with(_preload_content=False, body=expected_body)
    assert returned_identifier == mock_id


@pytest.mark.parametrize(
    "mock_api_method",
    [{"method_name": "api_v1_lists_list_list_identifier_copy_post_with_http_info"}],
    indirect=True,
)
def test_copy_list(client, mock_api_method, mock_id):
    existing_list_identifier = str(uuid.uuid4())

    returned_identifier = client.copy_list(existing_list_identifier)
    mock_api_method.assert_called_once_with(existing_list_identifier, _preload_content=False)
    assert returned_identifier == mock_id


@pytest.mark.parametrize(
    "mock_api_method",
    [{"method_name": "api_v1_lists_list_list_identifier_revise_post_with_http_info"}],
    indirect=True,
)
def test_revise_list(client, mock_api_method, mock_id):
    existing_list_identifier = str(uuid.uuid4())

    returned_identifier = client.revise_list(existing_list_identifier)

    mock_api_method.assert_called_once_with(existing_list_identifier, _preload_content=False)
    assert returned_identifier == mock_id
