from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch
import uuid

from ansys.grantami.serverapi_openapi.models import (
    GrantaServerApiListsDtoListBooleanCriterion,
    GrantaServerApiListsDtoListItem,
    GrantaServerApiListsDtoRecordListHeader,
    GrantaServerApiListsDtoRecordListSearchCriterion,
    GrantaServerApiListsDtoRecordListSearchResult,
    GrantaServerApiListsDtoUserOrGroup,
    GrantaServerApiListsDtoUserRole,
)
import pytest

from ansys.grantami.recordlists.models import (
    BooleanCriterion,
    RecordList,
    RecordListItem,
    SearchCriterion,
    SearchResult,
    User,
    UserRole,
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
        parent_record_list_identifier=None,
    )

    @pytest.fixture
    def record_list(self):
        record_list = RecordList(**self._data)
        return record_list

    @pytest.mark.parametrize("attr_name", list(_data.keys()))
    def test_record_list_is_read_only(self, record_list, attr_name):
        with pytest.raises(AttributeError):
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
        "parent_record_list_identifier",
    ]

    @pytest.mark.parametrize("attr_name", _optional_fields)
    def test_optional_parameters(self, attr_name):
        record_list_data = dict(**self._data)
        del record_list_data[attr_name]

        record_list = RecordList(**record_list_data)
        assert getattr(record_list, attr_name) is None

    @patch("ansys.grantami.recordlists.models.User")
    def test_dto_mapping(self, mock_user_class):
        # Overriding User.from_model method to a no-op. It is tested separately
        mock_user_class._from_model = lambda x: x
        # Using mock to generate unique values for each property
        mock_dto = Mock(spec=GrantaServerApiListsDtoRecordListHeader)
        record_list = RecordList._from_model(mock_dto)

        assert record_list.name is mock_dto.name
        assert record_list.identifier is mock_dto.identifier
        assert record_list.notes is mock_dto.notes
        assert record_list.description is mock_dto.description
        assert record_list.created_timestamp is mock_dto.created_timestamp
        assert record_list.created_user is mock_dto.created_user
        assert record_list.last_modified_timestamp is mock_dto.last_modified_timestamp
        assert record_list.last_modified_user is mock_dto.last_modified_user
        assert record_list.published_timestamp is mock_dto.published_timestamp
        assert record_list.published_user is mock_dto.published_user
        assert record_list.published is mock_dto.published
        assert record_list.is_revision is mock_dto.is_revision
        assert record_list.awaiting_approval is mock_dto.awaiting_approval
        assert record_list.internal_use is mock_dto.internal_use
        assert record_list.parent_record_list_identifier is mock_dto.parent_record_list_identifier


def test_user_dto_mapping():
    user_id = uuid.uuid4()
    username = "domain\\username"
    display_name = "domain\\displayname"
    dto_user = GrantaServerApiListsDtoUserOrGroup(user_id, display_name, username)

    user = User._from_model(dto_user)

    assert user.identifier == user_id
    assert user.name == username
    assert user.display_name == display_name


def test_record_list_item_from_dto_mapping():
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

    item = RecordListItem._from_model(dto_item)

    assert item.database_guid == db_guid
    assert item.table_guid == table_guid
    assert item.record_history_guid == record_history_guid
    assert item.record_version == record_version
    assert item.record_guid == record_guid


def test_record_list_item_to_dto_mapping():
    item = RecordListItem(
        database_guid=str(uuid.uuid4()),
        table_guid=str(uuid.uuid4()),
        record_history_guid=str(uuid.uuid4()),
        record_version=2,
    )
    item._record_guid = str(uuid.uuid4())

    dto = item._to_model()
    assert dto.database_guid == item.database_guid
    assert dto.table_guid == item.table_guid
    assert dto.record_history_guid == item.record_history_guid
    assert dto.record_version == item.record_version
    assert dto.record_guid is None


class TestItemEquality:
    DB1 = str(uuid.uuid4())
    T1 = str(uuid.uuid4())
    RHG1 = str(uuid.uuid4())
    RV1 = 1

    # Voluntary inconsistent naming scheme to highlight differences in test matrix
    db_guid_2 = str(uuid.uuid4())
    table_guid_2 = str(uuid.uuid4())
    record_hguid_2 = str(uuid.uuid4())
    record_version_2 = 2

    @pytest.mark.parametrize(
        ["item_a", "item_b", "expected_equal"],
        [
            (RecordListItem(DB1, T1, RHG1), RecordListItem(DB1, T1, RHG1), True),
            (RecordListItem(DB1, T1, RHG1), RecordListItem(DB1, T1, record_hguid_2), False),
            (RecordListItem(DB1, T1, RHG1), RecordListItem(DB1, table_guid_2, RHG1), False),
            (RecordListItem(DB1, T1, RHG1), RecordListItem(db_guid_2, T1, RHG1), False),
            (RecordListItem(DB1, T1, RHG1), RecordListItem(DB1, T1, RHG1, None), True),
            (RecordListItem(DB1, T1, RHG1, RV1), RecordListItem(DB1, T1, RHG1, RV1), True),
            (RecordListItem(DB1, T1, RHG1, RV1), RecordListItem(DB1, T1, RHG1, None), False),
            (
                RecordListItem(DB1, T1, RHG1, RV1),
                RecordListItem(DB1, T1, RHG1, record_version_2),
                False,
            ),
        ],
    )
    def test_item_equality(self, item_a, item_b, expected_equal):
        assert (item_a == item_b) is expected_equal

    def test_item_equality_with_other_type(self):
        item = RecordListItem(self.DB1, self.T1, self.RHG1)
        assert (item == 2) is False


class TestSearchCriterion:
    def test_search_criterion_dto_mapping(self):
        # Check one to one mapping between idiomatic class and DTO using ids of mock attributes
        criterion = Mock(spec=SearchCriterion)

        dto = SearchCriterion._to_model(criterion)

        assert isinstance(dto, GrantaServerApiListsDtoRecordListSearchCriterion)
        assert dto.name_contains is criterion.name_contains
        assert dto.user_role is criterion.user_role
        assert dto.is_published is criterion.is_published
        assert dto.is_awaiting_approval is criterion.is_awaiting_approval
        assert dto.is_internal_use is criterion.is_internal_use
        assert dto.is_revision is criterion.is_revision
        assert dto.contains_records_in_databases is criterion.contains_records_in_databases
        assert (
            dto.contains_records_in_integration_schemas
            is criterion.contains_records_in_integration_schemas
        )
        assert dto.contains_records_in_tables is criterion.contains_records_in_tables
        assert dto.contains_records is criterion.contains_records
        assert dto.user_can_add_or_remove_items is criterion.user_can_add_or_remove_items

    def test_simple_boolean_criterion_dto_mapping(self):
        crit_a_dto = Mock()
        crit_a = Mock(spec=SearchCriterion)
        crit_a.attach_mock(Mock(return_value=crit_a_dto), "_to_model")
        crit_b_dto = Mock()
        crit_b = Mock(spec=SearchCriterion)
        crit_b.attach_mock(Mock(return_value=crit_b_dto), "_to_model")

        criterion = BooleanCriterion(match_any=[crit_a], match_all=[crit_a, crit_b])

        dto = BooleanCriterion._to_model(criterion)

        assert dto.match_any == [crit_a_dto]
        assert dto.match_all == [crit_a_dto, crit_b_dto]

    def test_nested_boolean_criterion_dto_mapping(self):
        criterion = BooleanCriterion(
            match_any=[
                BooleanCriterion(
                    match_all=[
                        SearchCriterion(
                            name_contains="A",
                            user_role=UserRole.OWNER,
                        )
                    ],
                ),
            ]
        )

        criterion_dto = criterion._to_model()

        assert isinstance(criterion_dto, GrantaServerApiListsDtoListBooleanCriterion)
        assert criterion_dto.match_all is None
        assert len(criterion_dto.match_any) == 1
        nested_boolean_criterion = criterion_dto.match_any[0]
        assert isinstance(nested_boolean_criterion, GrantaServerApiListsDtoListBooleanCriterion)
        assert nested_boolean_criterion.match_any is None
        assert len(nested_boolean_criterion.match_all) == 1
        leaf_criterion = nested_boolean_criterion.match_all[0]
        assert isinstance(leaf_criterion, GrantaServerApiListsDtoRecordListSearchCriterion)
        assert leaf_criterion.name_contains == "A"
        assert leaf_criterion.user_role == GrantaServerApiListsDtoUserRole.OWNER


class TestSearchResult:
    @pytest.mark.parametrize("include_items", [True, False])
    def test_dto_mapping(self, monkeypatch, include_items):
        header_mock = Mock(spec=GrantaServerApiListsDtoRecordListHeader)
        item_1_mock = Mock(spec=GrantaServerApiListsDtoListItem)
        item_2_mock = Mock(spec=GrantaServerApiListsDtoListItem)
        search_result_dto = GrantaServerApiListsDtoRecordListSearchResult(
            header=header_mock, items=[item_1_mock, item_2_mock]
        )
        # Mock RecordListItem._from_model and RecordList._from_model to be able to assert that they
        # have been called with the expected args.
        item_from_model_mock = Mock()
        monkeypatch.setattr(RecordListItem, "_from_model", item_from_model_mock)
        record_list_from_model_mock = Mock()
        monkeypatch.setattr(RecordList, "_from_model", record_list_from_model_mock)

        search_result = SearchResult._from_model(search_result_dto, include_items)

        record_list_from_model_mock.assert_called_once_with(header_mock)
        if include_items:
            item_from_model_mock.assert_has_calls([call(item_1_mock), call(item_2_mock)])
        else:
            assert search_result.items is None
