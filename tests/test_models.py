from datetime import datetime
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
            identifier="00000",
            name="UnitTestList",
            created_timestamp=datetime.now(),
            published=False,
            awaiting_approval=False,
        )

    def test_read_items(self, mock_client, record_list):
        record_list.read_items()
        assert mock_client.get_list_items.called_once_with("00000")

    items_variations = pytest.mark.parametrize(
        "items", [[], None, ["1", 2], [RecordListItem("db", "table", "record")]]
    )

    @items_variations
    def test_add_items(self, mock_client, record_list, items):
        record_list.add_items(items)
        assert mock_client.add_items_to_list.called_once_with(items)

    @items_variations
    def test_remove_items(self, mock_client, record_list, items):
        record_list.add_items([])
        assert mock_client.add_items_to_list.called_once_with([])
