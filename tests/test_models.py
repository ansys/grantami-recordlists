from unittest.mock import Mock

import pytest

from ansys.grantami.recordlists._connection import RecordListApiClient
from ansys.grantami.recordlists.models import RecordList, RecordListItem


class TestRecordList:
    @pytest.fixture
    def mock_client(self):
        return Mock(spec=RecordListApiClient)

    @pytest.fixture
    def record_list(self, mock_client):
        return RecordList(
            mock_client,
            name="UnitTestList",
        )

    def test_read_items(self, mock_client, record_list):
        record_list.read_items()
        assert mock_client.get_list_items.called_once_with("00000")

    items_variations = pytest.mark.parametrize(
        "items", [[], ["1", 2], [RecordListItem("db", "table", "record")]]
    )

    @items_variations
    def test_add_items(self, mock_client, record_list, items):
        record_list.add_items(items)
        assert mock_client.add_items_to_list.called_once_with(items)

    @items_variations
    def test_remove_items(self, mock_client, record_list, items):
        record_list.add_items([])
        assert mock_client.add_items_to_list.called_once_with([])

    def test_create_minimal_list(self, mock_client):
        mock_id = "0000"
        mock_client._create_list = Mock(return_value=mock_id)
        list_name = "TestCreateFromRecordList"

        record_list = RecordList(mock_client, name=list_name)
        record_list.create()

        mock_client._create_list.assert_called_once_with(
            name=list_name,
            notes=None,
            description=None,
            items=None,
        )
        mock_client._get_list.assert_called_once_with(mock_id)
        mock_client.get_list_items.assert_not_called()

    def test_create_list_with_items(self, mock_client):
        mock_id = "0000"
        mock_client._create_list = Mock(return_value=mock_id)
        items = [RecordListItem("db", "table", "record")]
        list_name = "TestCreateFromRecordList"
        list_notes = "Notes"
        list_description = "Description"

        record_list = RecordList(
            mock_client,
            name=list_name,
            description=list_description,
            notes=list_notes,
            items=items,
        )
        record_list.create()

        mock_client._create_list.assert_called_once_with(
            name=list_name,
            items=items,
            notes=list_notes,
            description=list_description,
        )
        mock_client._get_list.assert_called_once_with(mock_id)
        mock_client.get_list_items.assert_called_once()
