import pytest

from ansys.openapi.common import ApiException
from ansys.grantami.recordlists.models import RecordList, RecordListItem

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


def test_create_minimal_list(admin_client, list_name):
    record_list_id = admin_client.create_list(name=list_name)

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


def test_copy_list(api_client, new_list_id):
    list_copy_identifier = api_client.copy_list(new_list_id)
    assert list_copy_identifier != new_list_id

    original_list = api_client.get_list(new_list_id)
    copied_list = api_client.get_list(list_copy_identifier)

    # Copied list name is original list name + " copy_{timestamp}"
    assert original_list.name in copied_list.name
    assert copied_list.description == original_list.description
    assert copied_list.notes == original_list.notes


def test_revise_unpublished_list(api_client, new_list_id):
    with pytest.raises(ApiException) as exc:
        api_client.revise_list(new_list_id)

    assert exc.value.status_code == 403


@pytest.mark.skip(reason="No functionality to publish list yet")
def test_revise_published_list(api_client, new_list_id):
    raise NotImplementedError


@pytest.mark.parametrize(
    ["create_client_name", "read_client_name"],
    [
        ("admin_client", "basic_client"),
        ("basic_client", "admin_client"),
    ],
)
def test_list_access(create_client_name, read_client_name, request, list_name):
    """Check that lists that are not published are only available to their creator."""
    create_client = request.getfixturevalue(create_client_name)
    read_client = request.getfixturevalue(read_client_name)
    list_id = create_client.create_list(name=list_name)

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
# TODO test lifecylce methods on revision
