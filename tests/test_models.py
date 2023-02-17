from unittest.mock import Mock
from datetime import datetime

import pytest

from ansys.grantami.recordlists._connection import RecordListApiClient
from ansys.grantami.recordlists.models import RecordList, RecordListItem, User


class TestRecordList:
    _list_name = "UnitTestList"
    _mock_id = "889dcaef-1ef4-4b92-8ff9-46f08d936f39"
    _mock_user = Mock(spec=User)

    @pytest.fixture
    def mock_client(self):
        return Mock(spec=RecordListApiClient)

    @pytest.fixture
    def new_list(self, mock_client):
        return RecordList(
            mock_client,
            name=self._list_name,
        )

    @pytest.fixture
    def existing_list(self, mock_client):
        record_list = RecordList(
            mock_client,
            name=self._list_name,
        )
        now = datetime.now()
        record_list._set_internal_state(
            identifier=self._mock_id,
            created_timestamp=now,
            created_user=self._mock_user,
            published=False,
            is_revision=False,
            awaiting_approval=False,
            internal_use=False,
            last_modified_timestamp=now,
            last_modified_user=self._mock_user,
            published_timestamp=now,
            published_user=self._mock_user,
        )
        return record_list

    def test_read_items(self, mock_client, new_list):
        with pytest.raises(RuntimeError):
            new_list.read_items()
        mock_client.get_list_items.assert_not_called()

    def test_read_items_existing_list(self, mock_client, existing_list):
        existing_list.read_items()
        mock_client.get_list_items.assert_called_once_with(self._mock_id)

    items_variations = pytest.mark.parametrize(
        "items", [[], ["1", 2], [RecordListItem("db", "table", "record")]]
    )

    @items_variations
    def test_add_items_new_list(self, mock_client, new_list, items):
        new_list.add_items(items)
        mock_client.add_items_to_list.assert_not_called()

    @items_variations
    def test_add_items_existing_list(self, mock_client, existing_list, items):
        existing_list.add_items(items)
        mock_client.add_items_to_list.assert_called_once_with(self._mock_id, items)

    # TODO test removing items not already in items
    def test_remove_items_new_list(self, mock_client, new_list):
        items = [RecordListItem("db", "table", "record")]
        new_list._items = items
        new_list.remove_items(items)
        mock_client.add_items_to_list.assert_not_called()
        assert new_list.items == []

    # TODO test removing items on existing list

    def test_create_minimal_list(self, mock_client, new_list):
        mock_client._create_list = Mock(return_value=self._mock_id)

        new_list.create()

        mock_client._create_list.assert_called_once_with(
            name=self._list_name,
            notes=None,
            description=None,
            items=None,
        )
        mock_client._get_list.assert_called_once_with(self._mock_id)
        mock_client.get_list_items.assert_not_called()

    def test_create_list_with_items_and_data(self, mock_client, new_list):
        mock_client._create_list = Mock(return_value=self._mock_id)
        items = [RecordListItem("db", "table", "record")]
        list_notes = "Notes"
        list_description = "Description"

        new_list.add_items(items)
        new_list.description = list_description
        new_list.notes = list_notes
        new_list.create()

        mock_client._create_list.assert_called_once_with(
            name=self._list_name,
            notes=list_notes,
            description=list_description,
            items=items,
        )

        mock_client._get_list.assert_called_once_with(self._mock_id)
        mock_client.get_list_items.assert_called_once()

    def test_delete_new_list(self, mock_client, new_list):
        with pytest.raises(RuntimeError):
            new_list.delete()
        mock_client.delete_list.assert_not_called()

    def test_delete_existing_list(self, mock_client, existing_list):
        existing_list.delete()
        mock_client.delete_list.assert_called_once_with(self._mock_id)
