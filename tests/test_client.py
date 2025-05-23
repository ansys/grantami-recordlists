# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock
import uuid

from ansys.grantami.serverapi_openapi.v2025r2 import models
from ansys.grantami.serverapi_openapi.v2025r2.api import (
    ListItemApi,
    ListManagementApi,
    ListPermissionsApi,
)
from ansys.grantami.serverapi_openapi.v2025r2.models import (
    GsaCreateListItem,
    GsaCreateRecordList,
    GsaCreateRecordListItemsInfo,
    GsaDeleteRecordListItem,
    GsaDeleteRecordListItems,
    GsaListItem,
    GsaRecordListHeader,
    GsaRecordListItemsInfo,
    GsaUpdateRecordListProperties,
    GsaUserPermission,
)
import pytest

from ansys.grantami.recordlists import (
    RecordList,
    RecordListItem,
    SearchResult,
)
from ansys.grantami.recordlists._connection import (
    PROXY_PATH,
    _RecordListsApiClient2025R2,
)


@pytest.fixture
def client(request):
    client = _RecordListsApiClient2025R2(
        session=Mock(),
        service_layer_url="http://server_name/mi_servicelayer",
        configuration=Mock(),
    )
    client.setup_client(models)
    return client


@pytest.fixture
def mock_list():
    guid = str(uuid.uuid4())
    record_list = Mock(spec=RecordList, identifier=guid)
    return record_list


def test_client_has_expected_api_url(client):
    assert client.api_url == "http://server_name/mi_servicelayer" + PROXY_PATH


def test_client_25r2_repr(client):
    assert repr(client) == "<_RecordListsApiClient2025R2 url: http://server_name/mi_servicelayer>"


class TestClientMethod:
    _return_value: Any
    _api_name: str
    _api_method: str
    _mock_uuid = str(uuid.uuid4())

    @pytest.fixture
    def api_method(self, monkeypatch):
        mocked_method = Mock(return_value=self._return_value)

        monkeypatch.setattr(self._api, self._api_method, mocked_method)
        return mocked_method


class TestReadList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "get_list"

    def test_read_list(self, client, api_method):
        identifier = str(uuid.uuid4())
        client.get_list(identifier)
        api_method.assert_called_once_with(list_identifier=identifier)


class TestReadAllLists(TestClientMethod):
    _return_value = SimpleNamespace(lists=[])
    _api = ListManagementApi
    _api_method = "get_all_lists"

    def test_read_all_lists(self, client, api_method):
        lists = client.get_all_lists()
        api_method.assert_called_once_with()
        assert lists == []


class TestReadItems(TestClientMethod):
    r_value = Mock(spec=GsaRecordListItemsInfo)
    r_value.items = []
    _return_value = r_value
    _api = ListItemApi
    _api_method = "get_list_items"

    def test_read_items(self, client, api_method, mock_list):
        items = client.get_list_items(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
        assert items == []


class TestAddItems(TestClientMethod):
    _api = ListItemApi
    _api_method = "add_items_to_list"

    _existing_dto_item = GsaListItem(
        database_guid=str(uuid.uuid4()),
        table_guid=str(uuid.uuid4()),
        record_history_guid=str(uuid.uuid4()),
        record_version=None,
    )
    _existing_item = RecordListItem._from_model(_existing_dto_item)

    @staticmethod
    def _convert_create_dto_to_item_dto(
        create_dto: GsaCreateListItem,
    ) -> GsaListItem:
        return GsaListItem(
            database_guid=create_dto.database_guid,
            record_history_guid=create_dto.record_history_guid,
            table_guid=create_dto.table_guid,
            record_version=create_dto.record_version,
        )

    @pytest.fixture
    def api_method(self, monkeypatch):
        def compute_result(list_identifier, body: GsaCreateRecordListItemsInfo):
            return GsaRecordListItemsInfo(
                items=[self._existing_dto_item]
                + [self._convert_create_dto_to_item_dto(i) for i in body.items]
            )

        mocked_method = Mock(side_effect=compute_result)
        monkeypatch.setattr(self._api, self._api_method, mocked_method)
        return mocked_method

    @pytest.mark.parametrize("items", [[], set()])
    def test_add_no_items(self, client, api_method, mock_list, items):
        response = client.add_items_to_list(mock_list, items)
        expected_body = GsaCreateRecordListItemsInfo(items=[])
        api_method.assert_called_once_with(list_identifier=mock_list.identifier, body=expected_body)
        assert response == [self._existing_item]

    def test_add_items(self, client, api_method, mock_list):
        new_item = RecordListItem("a", "b", "c")
        expected_body = GsaCreateRecordListItemsInfo(
            items=[
                GsaCreateListItem(
                    database_guid="a",
                    table_guid="b",
                    record_history_guid="c",
                    record_version=None,
                )
            ]
        )

        response = client.add_items_to_list(mock_list, [new_item])

        api_method.assert_called_once_with(list_identifier=mock_list.identifier, body=expected_body)
        assert response == [self._existing_item, new_item]

    def test_add_item_without_table_guids_raises_value_error(self, client, api_method, mock_list):
        new_item = RecordListItem("a", None, "c")
        with pytest.raises(ValueError, match="table_guid must be provided"):
            client.add_items_to_list(mock_list, [new_item])


class TestRemoveItems(TestClientMethod):
    _api = ListItemApi
    _api_method = "remove_items_from_list"

    _existing_dto_delete_item = GsaDeleteRecordListItem(
        database_guid=str(uuid.uuid4()),
        record_history_guid=str(uuid.uuid4()),
        record_version=None,
    )
    _table_guid = str(uuid.uuid4())
    _record_guid = str(uuid.uuid4())
    kwargs = _existing_dto_delete_item.to_dict() | {
        "table_guid": _table_guid,
        "record_guid": _record_guid,
    }
    _existing_dto_item = GsaListItem(**kwargs)

    _existing_item = RecordListItem._from_model(_existing_dto_item)

    @staticmethod
    def _compare_dtos(left: Any, right: Any) -> bool:
        result = True
        try:
            result &= left.database_guid == right.database_guid
            result &= left.record_history_guid == right.record_history_guid
            result &= left.record_version == right.record_version
        except AttributeError:
            return False
        return result

    @pytest.fixture
    def api_method(self, monkeypatch):
        def compute_result(list_identifier, body: GsaRecordListItemsInfo):
            # Naive, by reference, computation of items left after removal
            result_items = []
            if not any(self._compare_dtos(self._existing_dto_item, item) for item in body.items):
                result_items.append(self._existing_dto_item)
            return GsaRecordListItemsInfo(items=result_items)

        mocked_method = Mock(side_effect=compute_result)
        monkeypatch.setattr(self._api, self._api_method, mocked_method)
        return mocked_method

    @pytest.mark.parametrize("items", [[], set()])
    def test_remove_no_items(self, client, api_method, items, mock_list):
        response = client.remove_items_from_list(mock_list, items)

        expected_body = GsaDeleteRecordListItems(items=[])
        api_method.assert_called_once_with(list_identifier=mock_list.identifier, body=expected_body)
        existing_item = RecordListItem._from_model(self._existing_dto_item)
        assert response == [existing_item]

    def test_remove_items(self, client, api_method, mock_list):
        items = [self._existing_item]
        expected_body = GsaDeleteRecordListItems(
            items=[self._existing_dto_delete_item],
        )

        response = client.remove_items_from_list(mock_list, items)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier, body=expected_body)
        assert response == []


class TestDeleteList(TestClientMethod):
    _return_value = None
    _api = ListManagementApi
    _api_method = "delete_list"

    def test_delete_list(self, client, api_method, mock_list):
        client.delete_list(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)


class TestUpdate(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "update_list"

    def test_update_list_no_args(self, client, api_method, mock_list):
        with pytest.raises(ValueError, match="at least one property"):
            client.update_list(mock_list)
        api_method.assert_not_called()

    def test_update_list_single_non_nullable_args(self, client, api_method, mock_list):
        with pytest.raises(ValueError):
            client.update_list(mock_list, name=None)
        api_method.assert_not_called()

    @pytest.mark.parametrize("prop_name", ["name"])
    @pytest.mark.parametrize("prop_value", ["Some text"])
    def test_update_list_non_nullable_args_with_value(
        self,
        client,
        api_method,
        mock_list,
        prop_name,
        prop_value,
    ):
        client.update_list(mock_list, **{prop_name: prop_value})
        expected_body = GsaUpdateRecordListProperties(
            **{prop_name: prop_value},
        )
        api_method.assert_called_once_with(list_identifier=mock_list.identifier, body=expected_body)

    @pytest.mark.parametrize("prop_name", ["notes", "description"])
    @pytest.mark.parametrize("prop_value", [None, "Some text"])
    def test_update_list_single_nullable_args(
        self, client, api_method, mock_list, prop_name, prop_value
    ):
        client.update_list(mock_list, **{prop_name: prop_value})
        expected_body = GsaUpdateRecordListProperties(
            **{prop_name: prop_value},
        )
        api_method.assert_called_once_with(list_identifier=mock_list.identifier, body=expected_body)


class TestPublishList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "publish_list"

    def test_publish_list(self, client, api_method, mock_list):
        updated_list = client.publish_list(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
        assert isinstance(updated_list, RecordList)


class TestUnpublishList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "unpublish_list"

    def test_unpublish_list(self, client, api_method, mock_list):
        updated_list = client.unpublish_list(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
        assert isinstance(updated_list, RecordList)


class TestResetApprovalList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "reset_awaiting_approval"

    def test_reset_approval(self, client, api_method, mock_list):
        updated_list = client.cancel_list_approval_request(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
        assert isinstance(updated_list, RecordList)


class TestRequestApprovalList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "request_approval"

    def test_request_approval(self, client, api_method, mock_list):
        updated_list = client.request_list_approval(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
        assert isinstance(updated_list, RecordList)


class TestCreateList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "create_list"

    def test_create_list(self, client, api_method):
        list_name = "ListName"

        returned_list = client.create_list(list_name, items=[])

        expected_body = GsaCreateRecordList(
            name=list_name,
            description=None,
            notes=None,
            items=GsaCreateRecordListItemsInfo(items=[]),
        )
        api_method.assert_called_once_with(body=expected_body)
        assert isinstance(returned_list, RecordList)

    def test_create_list_with_items(self, client, api_method, unresolvable_item):
        list_name = "ListName"

        returned_list = client.create_list(list_name, items=[unresolvable_item])

        expected_body = GsaCreateRecordList(
            name=list_name,
            description=None,
            notes=None,
            items=GsaCreateRecordListItemsInfo(
                items=[
                    GsaCreateListItem(
                        database_guid=unresolvable_item.database_guid,
                        record_history_guid=unresolvable_item.record_history_guid,
                        table_guid=unresolvable_item.table_guid,
                        record_version=None,
                    )
                ]
            ),
        )
        api_method.assert_called_once_with(body=expected_body)
        assert isinstance(returned_list, RecordList)


class TestCopyList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "copy_list"

    def test_copy_list(self, client, api_method, mock_list):
        returned_list = client.copy_list(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
        assert isinstance(returned_list, RecordList)


class TestReviseList(TestClientMethod):
    _return_value = Mock(spec=GsaRecordListHeader)
    _api = ListManagementApi
    _api_method = "revise_list"

    def test_revise_list(self, client, api_method, mock_list):
        returned_list = client.revise_list(mock_list)
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
        assert isinstance(returned_list, RecordList)


class TestSearch:
    @pytest.fixture
    def search_result_id(self):
        return str(uuid.uuid4())

    @pytest.fixture
    def mock_search_post(self, monkeypatch, search_result_id):
        response = models.GsaRecordListSearchInfo(
            search_result_identifier=search_result_id,
        )
        mocked_method = Mock(return_value=response)
        monkeypatch.setattr(ListManagementApi, "run_record_lists_search", mocked_method)
        return mocked_method

    @pytest.fixture
    def mock_search_result_get(self, monkeypatch):
        mock_search_result_info = Mock(spec=models.GsaRecordListSearchResultsInfo)
        mock_search_result = Mock(spec=models.GsaRecordListSearchResult)
        mock_search_result_info.search_results = [mock_search_result]
        mock_search_result.items = [Mock(spec=models.GsaListItem)]
        mocked_method = Mock(return_value=mock_search_result_info)
        monkeypatch.setattr(
            ListManagementApi,
            "get_record_list_search_results",
            mocked_method,
        )
        return mocked_method

    @pytest.mark.parametrize("include_items", [True, False])
    def test_search(
        self,
        client,
        mock_search_post,
        mock_search_result_get,
        search_result_id,
        monkeypatch,
        include_items,
    ):
        criterion_dto = Mock()
        to_model_method = Mock(return_value=criterion_dto)
        criterion = Mock()
        criterion.attach_mock(to_model_method, "_to_model")

        mock_from_model = Mock()
        monkeypatch.setattr(SearchResult, "_from_model", mock_from_model)

        results = client.search_for_lists(criterion, include_items=include_items)

        to_model_method.assert_called_once()
        expected_body = models.GsaRecordListSearchRequest(
            search_criterion=criterion_dto,
            response_options=models.GsaResponseOptions(
                include_record_list_items=include_items,
            ),
        )
        mock_search_post.assert_called_once_with(body=expected_body)
        mock_search_result_get.assert_called_once_with(result_resource_identifier=search_result_id)
        mock_from_model.assert_called_once_with(
            mock_search_result_get._mock_return_value.search_results[0], include_items
        )


class TestSubscribe(TestClientMethod):
    _return_value = Mock(spec=GsaUserPermission)
    _api = ListPermissionsApi
    _api_method = "subscribe"

    def test_subscribe(self, client, api_method, mock_list):
        response = client.subscribe_to_list(mock_list)
        assert response is None
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)


class TestUnsubscribe(TestClientMethod):
    _return_value = Mock(spec=GsaUserPermission)
    _api = ListPermissionsApi
    _api_method = "unsubscribe"

    def test_subscribe(self, client, api_method, mock_list):
        response = client.unsubscribe_from_list(mock_list)
        assert response is None
        api_method.assert_called_once_with(list_identifier=mock_list.identifier)
