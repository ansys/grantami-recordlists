import uuid

from ansys.openapi.common import ApiException
import pytest

from ansys.grantami.recordlists.models import (
    BooleanCriterion,
    RecordList,
    RecordListItem,
    SearchCriterion,
    UserRole,
)

pytestmark = pytest.mark.integration


def test_getting_all_lists(admin_client, new_list_id):
    # Using new_list_id fixture to ensure there is at least one list when this test is run
    all_lists = admin_client.get_all_lists()
    assert isinstance(all_lists, list)
    assert all(isinstance(l, RecordList) for l in all_lists)
    my_list = next(rl for rl in all_lists if rl.identifier == new_list_id)


def test_get_list_items(admin_client, new_list_with_items):
    record_list_items = admin_client.get_list_items(new_list_with_items)

    assert isinstance(record_list_items, list)
    assert all(isinstance(item, RecordListItem) for item in record_list_items)


def test_create_minimal_list(admin_client, cleanup_admin, list_name):
    record_list_id = admin_client.create_list(name=list_name)
    cleanup_admin.append(record_list_id)

    record_list = admin_client.get_list(record_list_id)
    assert record_list.name == list_name
    assert record_list.notes is None
    assert record_list.description is None
    assert isinstance(record_list.identifier, str)


@pytest.mark.parametrize("new_list_id", [{"cleanup": False}], indirect=True)
def test_delete_list(admin_client, new_list_id, list_name):
    admin_client.delete_list(new_list_id)

    with pytest.raises(ApiException) as exc:
        my_list = admin_client.get_list(new_list_id)
    assert exc.value.status_code == 404


def test_update_list(admin_client, new_list_id):
    admin_client.update_list(new_list_id, name="NEWUPDATEDNAME")
    record_list = admin_client.get_list(new_list_id)
    assert record_list.name == "NEWUPDATEDNAME"


def test_update_list_nullable_property(admin_client, new_list_id):
    admin_client.update_list(new_list_id, notes="Some notes")
    record_list = admin_client.get_list(new_list_id)
    assert record_list.notes == "Some notes"

    admin_client.update_list(new_list_id, notes=None)
    record_list = admin_client.get_list(new_list_id)
    assert record_list.notes is None


def test_copy_list(admin_client, cleanup_admin, new_list_id):
    list_copy_identifier = admin_client.copy_list(new_list_id)
    cleanup_admin.append(list_copy_identifier)
    assert list_copy_identifier != new_list_id

    original_list = admin_client.get_list(new_list_id)
    copied_list = admin_client.get_list(list_copy_identifier)

    # Copied list name is original list name + " copy_{timestamp}"
    assert original_list.name in copied_list.name
    assert copied_list.description == original_list.description
    assert copied_list.notes == original_list.notes


def test_revise_unpublished_list(admin_client, new_list_id):
    with pytest.raises(ApiException) as exc:
        admin_client.revise_list(new_list_id)

    assert exc.value.status_code == 403


@pytest.mark.parametrize(
    ["create_client_name", "read_client_name", "cleanup_fixture"],
    [
        ("admin_client", "basic_client", "cleanup_admin"),
        ("basic_client", "admin_client", "cleanup_basic"),
    ],
)
def test_list_access(create_client_name, read_client_name, request, list_name, cleanup_fixture):
    """Check that lists that are not published are only available to their creator."""
    create_client = request.getfixturevalue(create_client_name)
    read_client = request.getfixturevalue(read_client_name)
    cleanup = request.getfixturevalue(cleanup_fixture)
    list_id = create_client.create_list(name=list_name)
    cleanup.append(list_id)

    with pytest.raises(ApiException) as e:
        read_client.get_list(list_id)
    assert e.value.status_code == 403


class TestLifeCycle:
    _not_awaiting_approval_error = "The list is not currently awaiting approval."
    _already_awaiting_approval_error = "The list is already awaiting approval."


class TestLifeCycleNewList(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = False, published = False
    """

    def test_cannot_publish(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.publish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_withdraw(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.unpublish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_reset(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.reset_approval_request(new_list_id)
        assert e.value.status_code == 400

    def test_can_request_approval(self, admin_client, new_list_id):
        admin_client.request_approval(new_list_id)
        list_details = admin_client.get_list(new_list_id)
        assert list_details.awaiting_approval is True


class TestLifeCycleAwaitingApprovalAndNotPublished(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = True, published = False
    """

    @pytest.fixture(autouse=True)
    def request_approval_for_list(self, admin_client, new_list_id):
        admin_client.request_approval(new_list_id)

    def test_can_publish(self, admin_client, new_list_id):
        admin_client.publish(new_list_id)
        list_details = admin_client.get_list(new_list_id)
        assert list_details.awaiting_approval is False
        assert list_details.published is True
        assert list_details.published_timestamp is not None
        assert list_details.published_user is not None

    def test_cannot_withdraw(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match="not currently published") as e:
            admin_client.unpublish(new_list_id)
        assert e.value.status_code == 400

    def test_can_reset(self, admin_client, new_list_id):
        admin_client.reset_approval_request(new_list_id)
        list_details = admin_client.get_list(new_list_id)
        assert list_details.awaiting_approval is False

    def test_cannot_request_approval(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._already_awaiting_approval_error) as e:
            admin_client.request_approval(new_list_id)
        assert e.value.status_code == 400


class TestLifeCyclePublishedAndNotAwaitingApproval(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = False, published = True
    """

    @pytest.fixture(autouse=True)
    def publish_list(self, admin_client, new_list_id):
        admin_client.request_approval(new_list_id)
        admin_client.publish(new_list_id)

    def test_cannot_publish(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.publish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_withdraw(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.unpublish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_reset(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.reset_approval_request(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_request_approval(self, admin_client, new_list_id):
        admin_client.request_approval(new_list_id)
        list_details = admin_client.get_list(new_list_id)
        assert list_details.awaiting_approval is True
        assert list_details.published is True


class TestRevisionLifeCycle(TestLifeCyclePublishedAndNotAwaitingApproval):
    # Inherits the auto-use fixture to publish the list

    def test_revise_published_list(self, admin_client, new_list_id):
        revision_id = admin_client.revise_list(new_list_id)
        list_details = admin_client.get_list(revision_id)
        assert list_details.published is False
        assert list_details.awaiting_approval is False
        assert list_details.parent_record_list_identifier == new_list_id

        updated_note = "Notes added to list revision"
        _ = admin_client.update_list(revision_id, notes=updated_note)

        admin_client.request_approval(revision_id)
        admin_client.publish(revision_id)

        with pytest.raises(ApiException) as e:
            revision_list_details = admin_client.get_list(revision_id)
        e.value.status_code == 404

        original_list_details = admin_client.get_list(new_list_id)
        assert original_list_details.notes == updated_note


class TestLifeCyclePublishedAndAwaitingApproval(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = True, published = True
    """

    @pytest.fixture(autouse=True)
    def publish_and_request_approval_for_list(self, admin_client, new_list_id):
        # TODO refactor if we allow creating lists with predefined statuses
        admin_client.request_approval(new_list_id)
        admin_client.publish(new_list_id)
        admin_client.request_approval(new_list_id)

    def test_cannot_publish(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match="already published") as e:
            admin_client.publish(new_list_id)
        assert e.value.status_code == 400

    def test_can_withdraw(self, admin_client, new_list_id):
        admin_client.unpublish(new_list_id)
        list_details = admin_client.get_list(new_list_id)
        assert list_details.published is False
        assert list_details.awaiting_approval is False

    def test_can_reset(self, admin_client, new_list_id):
        admin_client.reset_approval_request(new_list_id)
        list_details = admin_client.get_list(new_list_id)
        assert list_details.awaiting_approval is False
        assert list_details.published is True

    def test_cannot_request_approval(self, admin_client, new_list_id):
        with pytest.raises(ApiException, match=self._already_awaiting_approval_error) as e:
            admin_client.request_approval(new_list_id)
        assert e.value.status_code == 400


# TODO test published list cannot be updated (properties or items)


class TestSearch:
    """Exercises some search criteria."""

    _name_suffix_A = "_ListA"
    _name_suffix_B = "_ListB"
    _name_suffix_C = "_ListC"

    @pytest.fixture(scope="class")
    def list_a(self, admin_client, list_name):
        """A personal list with a known name."""
        list_id = admin_client.create_list(list_name + self._name_suffix_A)
        yield list_id
        admin_client.delete_list(list_id)

    @pytest.fixture(scope="class")
    def list_b(self, admin_client, list_name):
        """A published list with a known name."""
        list_id = admin_client.create_list(list_name + self._name_suffix_B)
        admin_client.request_approval(list_id)
        admin_client.publish(list_id)
        yield list_id
        admin_client.delete_list(list_id)

    @pytest.fixture(scope="class")
    def list_c(self, admin_client, list_name, list_b, example_item):
        """A revision of list B with a known name and items."""
        list_id = admin_client.revise_list(list_b)
        admin_client.update_list(list_id, name=list_name + self._name_suffix_C)
        admin_client.add_items_to_list(list_id, [example_item])
        yield list_id
        admin_client.delete_list(list_id)

    @pytest.fixture(scope="class", autouse=True)
    def multiple_lists(self, list_a, list_b, list_c):
        yield list_a, list_b, list_c

    def test_search_list_name_match_all(self, admin_client, list_name):
        # All tests include name_contains=list_name to filter results to lists created in this test
        #  session.
        criteria = SearchCriterion(name_contains=list_name)
        results = admin_client.search(criteria)
        assert len(results) == 3

    def test_search_list_name_match_one(self, admin_client, list_a):
        criteria = SearchCriterion(name_contains=self._name_suffix_A)
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_a

    def test_search_not_published_or_awaiting(self, admin_client, list_a):
        criteria = SearchCriterion(
            name_contains=self._name_suffix_A,
            is_published=False,
            is_awaiting_approval=False,
            is_revision=False,
            is_internal_use=False,
        )
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_a

    def test_search_published(self, admin_client, list_name, list_b):
        criteria = SearchCriterion(name_contains=list_name, is_published=True)
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_b

    def test_search_revision(self, admin_client, list_name, list_c):
        criteria = SearchCriterion(name_contains=list_name, is_revision=True)
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_c

    def test_search_by_database(self, admin_client, list_name, example_item, list_c):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_databases=[example_item.database_guid],
        )
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_c

    def test_search_by_multiple_databases(self, admin_client, list_name, example_item, list_c):
        # List of databases = Is in one OR the other
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_databases=[example_item.database_guid, str(uuid.uuid4())],
        )
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_c

    def test_search_by_table(self, admin_client, list_name, example_item, list_c):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_tables=[example_item.table_guid],
        )
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_c

    def test_search_by_record(self, admin_client, list_name, example_item, list_c):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records=[example_item.record_history_guid],
        )
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_c

    def test_search_role_is_none(self, admin_client, list_name):
        criteria = SearchCriterion(user_role=UserRole.NONE)
        results = admin_client.search(criteria)
        assert len(results) == 0
        # TODO: Perhaps not worth keeping None as a value. Check what it's meant to be.

    def test_search_role_is_owner(self, admin_client, list_name):
        criteria = SearchCriterion(name_contains=list_name, user_role=UserRole.OWNER)
        results = admin_client.search(criteria)
        assert len(results) == 3

    def test_match_all(self, admin_client, list_name, new_list_id, list_a):
        # Uses fixture new_list_id to create a list with the root name only and assert that the
        # match_all criteria is excluding it as expected.
        criteria = BooleanCriterion(
            match_all=[
                SearchCriterion(name_contains=list_name),
                SearchCriterion(name_contains=self._name_suffix_A),
            ]
        )
        results = admin_client.search(criteria)
        assert len(results) == 1
        assert results[0].identifier == list_a

    def test_nested_boolean_criteria(self, admin_client, list_name, new_list_id, list_a, list_b):
        criteria = BooleanCriterion(
            match_any=[
                # Should match A only
                BooleanCriterion(
                    match_all=[
                        SearchCriterion(name_contains=list_name),
                        SearchCriterion(name_contains=self._name_suffix_A),
                    ]
                ),
                # Should match B only
                BooleanCriterion(
                    match_all=[
                        SearchCriterion(name_contains=list_name),
                        SearchCriterion(name_contains=self._name_suffix_B),
                        SearchCriterion(is_published=True),
                    ]
                ),
            ]
        )
        results = admin_client.search(criteria)
        assert len(results) == 2
        ids = {result.identifier for result in results}
        assert list_a in ids
        assert list_b in ids

    @pytest.fixture(scope="function")
    def list_a_suffix_only(self, admin_client, unique_id, cleanup_admin):
        list_id = admin_client.create_list(name=f"{unique_id}{self._name_suffix_A}")
        cleanup_admin.append(list_id)
        yield list_id

    def test_boolean_match_any_and_all_is_not_OR(
        self,
        admin_client,
        list_name,
        new_list_id,
        list_a,
        list_b,
        list_c,
        list_a_suffix_only,
    ):
        # If it was OR, we'd have 5 result: all lists created as fixtures
        criteria = BooleanCriterion(
            match_any=[
                SearchCriterion(name_contains=self._name_suffix_A),
            ],
            match_all=[SearchCriterion(name_contains=list_name)],
        )
        results = admin_client.search(criteria)
        ids = {result.identifier for result in results}
        assert new_list_id in ids
        assert list_a in ids
        assert list_b in ids
        assert list_c in ids
        assert list_a_suffix_only not in ids
        assert len(results) == 4

    def test_boolean_match_any_and_all_is_not_AND(
        self,
        admin_client,
        list_name,
        new_list_id,
        list_a,
        list_b,
        list_c,
        list_a_suffix_only,
    ):
        # If it was AND, we'd have 1 result: list_a
        criteria = BooleanCriterion(
            match_any=[
                SearchCriterion(name_contains=self._name_suffix_A),
            ],
            match_all=[SearchCriterion(name_contains=list_name)],
        )
        results = admin_client.search(criteria)
        ids = {result.identifier for result in results}
        assert new_list_id in ids
        assert list_a in ids
        assert list_b in ids
        assert list_c in ids
        assert list_a_suffix_only not in ids
        assert len(results) == 4

    def test_boolean_match_all_takes_precedence(
        self,
        admin_client,
        list_name,
        new_list_id,
        list_a,
        list_b,
        list_c,
        list_a_suffix_only,
    ):
        criteria = BooleanCriterion(
            match_any=[
                SearchCriterion(name_contains=list_name),
            ],
            match_all=[SearchCriterion(name_contains=self._name_suffix_A)],
        )
        results = admin_client.search(criteria)
        ids = {result.identifier for result in results}
        assert new_list_id not in ids
        assert list_a in ids
        assert list_b not in ids
        assert list_c not in ids
        assert list_a_suffix_only in ids
        assert len(results) == 2
