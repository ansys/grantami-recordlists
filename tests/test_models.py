import uuid
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import pytest

from ansys.grantami.recordlists.models import RecordList, RecordListItem, User
from ansys.grantami.serverapi_openapi.models import (
    GrantaServerApiListsDtoRecordListHeader,
    GrantaServerApiListsDtoUserOrGroup,
    GrantaServerApiListsDtoListItem,
)


class TestRecordList:
    _list_name = "UnitTestList"
    _mock_id = "889dcaef-1ef4-4b92-8ff9-46f08d936f39"
    _mock_user = Mock(spec=User)

    _notes = "TestNotes"
    _description = "TestDescription"
    _last_modified_timestamp = datetime.now() - timedelta(days=1)
    _created_timestamp = datetime.now() - timedelta(days=2)
    _published_timestamp = datetime.now()

    _data = dict(
        name=_list_name,
        identifier=_mock_id,
        created_timestamp=_created_timestamp,
        created_user=_mock_user,
        published=False,
        is_revision=False,
        awaiting_approval=False,
        internal_use=False,
        notes=_notes,
        description=_description,
        last_modified_timestamp=_last_modified_timestamp,
        last_modified_user=_mock_user,
        published_timestamp=_published_timestamp,
        published_user=_mock_user,
    )

    @pytest.fixture
    def record_list(self):
        record_list = RecordList(**self._data)
        return record_list

    @pytest.mark.parametrize("attr_name", list(_data.keys()))
    def test_record_list_is_read_only(self, record_list, attr_name):
        with pytest.raises(AttributeError, match="can't set attribute"):
            setattr(record_list, attr_name, "new_value")

    _required_fields = [
        "name",
        "identifier",
        "created_timestamp",
        "created_user",
        "published",
        "is_revision",
        "awaiting_approval",
        "internal_use",
    ]

    @pytest.mark.parametrize("attr_name", _required_fields)
    def test_required_properties(self, attr_name):
        record_list_data = dict(**self._data)
        del record_list_data[attr_name]

        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            RecordList(**record_list_data)

    _optional_fields = [
        "notes",
        "description",
        "last_modified_timestamp",
        "last_modified_user",
        "published_timestamp",
        "published_user",
    ]

    @pytest.mark.parametrize("attr_name", _optional_fields)
    def test_optional_parameters(self, attr_name):
        record_list_data = dict(**self._data)
        del record_list_data[attr_name]

        record_list = RecordList(**record_list_data)
        assert getattr(record_list, attr_name) is None

    @patch("ansys.grantami.recordlists.models.User")
    def test_dto_mapping(self, mock_user_class):
        # Ignoring sub-mapping, just checking that fields are correctly mapped. User.from_model is
        # tested separately
        mock_user_class.from_model = lambda x: x
        # Using mock to generate unique values for each property
        mock_dto = Mock(spec=GrantaServerApiListsDtoRecordListHeader)
        record_list = RecordList.from_model(mock_dto)

        assert record_list.name == mock_dto.name
        assert record_list.identifier == mock_dto.identifier
        assert record_list.notes == mock_dto.notes
        assert record_list.description == mock_dto.description
        assert record_list.created_timestamp == mock_dto.created_timestamp
        assert record_list.created_user == mock_dto.created_user
        assert record_list.last_modified_timestamp == mock_dto.last_modified_timestamp
        assert record_list.last_modified_user == mock_dto.last_modified_user
        assert record_list.published_timestamp == mock_dto.published_timestamp
        assert record_list.published_user == mock_dto.published_user
        assert record_list.published is mock_dto.published
        assert record_list.is_revision is mock_dto.is_revision
        assert record_list.awaiting_approval is mock_dto.awaiting_approval
        assert record_list.internal_use is mock_dto.internal_use


def test_user_dto_mapping():
    user_id = uuid.uuid4()
    username = "domain\\username"
    display_name = "domain\\displayname"
    dto_user = GrantaServerApiListsDtoUserOrGroup(user_id, display_name, username)

    user = User.from_model(dto_user)

    assert user.identifier == user_id
    assert user.name == username
    assert user.display_name == display_name


def test_record_list_item_dto_mapping():
    db_guid = uuid.uuid4()
    table_guid = uuid.uuid4()
    record_history_guid = uuid.uuid4()
    record_version = 1
    record_guid = uuid.uuid4()

    dto_item = GrantaServerApiListsDtoListItem(
        database_guid=db_guid,
        table_guid=table_guid,
        record_history_guid=record_history_guid,
        record_version=record_version,
        record_guid=record_guid,
    )

    item = RecordListItem.from_model(dto_item)

    assert item.database_guid == db_guid
    assert item.table_guid == table_guid
    assert item.record_history_guid == record_history_guid
