import os
import uuid

import pytest

from ansys.openapi.common import ApiException
from ansys.grantami.recordlists import Connection
from ansys.grantami.recordlists.models import RecordList, RecordListItem


pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def sl_url():
    return os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")


@pytest.fixture(scope="session")
def list_admin_username():
    return os.getenv("TEST_LIST_ADMIN_USER")


@pytest.fixture(scope="session")
def list_admin_password():
    return os.getenv("TEST_LIST_ADMIN_PASS")


@pytest.fixture(scope="session")
def api_client(sl_url, list_admin_username, list_admin_password, list_name):
    """
    Fixture providing a real ApiClient to run integration tests against an instance of Granta MI
    Server API.
    On teardown, deletes all lists named using the fixture `list_name`.
    """
    connection = Connection(f"{sl_url}/proxy/v1.svc").with_credentials(
        list_admin_username, list_admin_password
    )
    client = connection.connect()
    yield client

    all_lists = client.get_all_lists()
    for record_list in all_lists:
        if record_list.name == list_name:
            client.delete_list(record_list.identifier)


@pytest.fixture(scope="session")
def list_name():
    """
    Provides a name for new lists. All lists created with this name are deleted on teardown of
    `api_client`.
    """
    prefix = "IntegrationTestList"
    _uuid = uuid.uuid4()
    return f"{prefix}_{_uuid}"


@pytest.fixture
def new_list_id(api_client, request, list_name):
    """
    Provides the identifier of newly created list.
    The created list include the name of the calling test as a `description`.
    """
    list_id = api_client.create_list(name=list_name, description=request.node.name)
    cleanup = getattr(request, "param", {}).get("cleanup", True)
    yield list_id
    if cleanup:
        api_client.delete_list(list_id)


@pytest.fixture
def new_list_with_items(api_client, new_list_id):
    items = [
        RecordListItem(
            "e595fe23-b450-4d18-8c08-4a0f378ef095",
            "81dff531-0254-4fbe-9621-174b10aaee3d",
            "3bc2b82f-0199-4f3b-a7af-8d520250b180",
        )
    ]
    api_client.add_items_to_list(new_list_id, items)
    return new_list_id


def test_getting_all_lists(api_client, new_list_id):
    # Using new_list_id fixture to ensure there is at least one list when this test is run
    all_lists = api_client.get_all_lists()
    assert isinstance(all_lists, list)
    assert all(isinstance(l, RecordList) for l in all_lists)
    my_list = next(rl for rl in all_lists if rl.identifier == new_list_id)


def test_get_list_items(api_client, new_list_with_items):
    record_list_items = api_client.get_list_items(new_list_with_items)

    assert isinstance(record_list_items, list)
    assert all(isinstance(item, RecordListItem) for item in record_list_items)


def test_create_minimal_list(api_client, list_name):
    record_list_id = api_client.create_list(name=list_name)

    record_list = api_client.get_list(record_list_id)
    assert record_list.name == list_name
    assert record_list.notes is None
    assert record_list.description is None
    assert isinstance(record_list.identifier, str)


@pytest.mark.parametrize("new_list_id", [{"cleanup": False}], indirect=True)
def test_delete_list(api_client, new_list_id, list_name):
    api_client.delete_list(new_list_id)

    with pytest.raises(ApiException) as exc:
        my_list = api_client.get_list(new_list_id)
    assert exc.value.status_code == 404


def test_update_list(api_client, new_list_id):
    api_client.update_list(new_list_id, name="NEWUPDATEDNAME")
    record_list = api_client.get_list(new_list_id)
    assert record_list.name == "NEWUPDATEDNAME"


def test_update_list_nullable_property(api_client, new_list_id):
    api_client.update_list(new_list_id, notes="Some notes")
    record_list = api_client.get_list(new_list_id)
    assert record_list.notes == "Some notes"

    api_client.update_list(new_list_id, notes=None)
    record_list = api_client.get_list(new_list_id)
    assert record_list.notes is None


class TestLifeCycle:
    _not_awaiting_approval_error = "The list is not currently awaiting approval."
    _already_awaiting_approval_error = "The list is already awaiting approval."


class TestLifeCycleNewList(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = False, published = False
    """

    def test_cannot_publish(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            api_client.publish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_withdraw(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            api_client.unpublish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_reset(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            api_client.reset_approval_request(new_list_id)
        assert e.value.status_code == 400

    def test_can_request_approval(self, api_client, new_list_id):
        api_client.request_approval(new_list_id)
        list_details = api_client.get_list(new_list_id)
        assert list_details.awaiting_approval is True


class TestLifeCycleAwaitingApprovalAndNotPublished(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = True, published = False
    """

    @pytest.fixture(autouse=True)
    def request_approval_for_list(self, api_client, new_list_id):
        api_client.request_approval(new_list_id)

    def test_can_publish(self, api_client, new_list_id):
        api_client.publish(new_list_id)
        list_details = api_client.get_list(new_list_id)
        assert list_details.awaiting_approval is False
        assert list_details.published is True
        assert list_details.published_timestamp is not None
        assert list_details.published_user is not None

    def test_cannot_withdraw(self, api_client, new_list_id):
        with pytest.raises(ApiException, match="not currently published") as e:
            api_client.unpublish(new_list_id)
        assert e.value.status_code == 400

    def test_can_reset(self, api_client, new_list_id):
        api_client.reset_approval_request(new_list_id)
        list_details = api_client.get_list(new_list_id)
        assert list_details.awaiting_approval is False

    def test_cannot_request_approval(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._already_awaiting_approval_error) as e:
            api_client.request_approval(new_list_id)
        assert e.value.status_code == 400


class TestLifeCyclePublishedAndNotAwaitingApproval(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = False, published = True
    """

    @pytest.fixture(autouse=True)
    def publish_list(self, api_client, new_list_id):
        api_client.request_approval(new_list_id)
        api_client.publish(new_list_id)

    def test_cannot_publish(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            api_client.publish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_withdraw(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            api_client.unpublish(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_reset(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            api_client.reset_approval_request(new_list_id)
        assert e.value.status_code == 400

    def test_cannot_request_approval(self, api_client, new_list_id):
        api_client.request_approval(new_list_id)
        list_details = api_client.get_list(new_list_id)
        assert list_details.awaiting_approval is True
        assert list_details.published is True


class TestLifeCyclePublishedAndAwaitingApproval(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = True, published = True
    """

    @pytest.fixture(autouse=True)
    def publish_and_request_approval_for_list(self, api_client, new_list_id):
        # TODO refactor if we allow creating lists with predefined statuses
        api_client.request_approval(new_list_id)
        api_client.publish(new_list_id)
        api_client.request_approval(new_list_id)

    def test_cannot_publish(self, api_client, new_list_id):
        with pytest.raises(ApiException, match="already published") as e:
            api_client.publish(new_list_id)
        assert e.value.status_code == 400

    def test_can_withdraw(self, api_client, new_list_id):
        api_client.unpublish(new_list_id)
        list_details = api_client.get_list(new_list_id)
        assert list_details.published is False
        assert list_details.awaiting_approval is False

    def test_can_reset(self, api_client, new_list_id):
        api_client.reset_approval_request(new_list_id)
        list_details = api_client.get_list(new_list_id)
        assert list_details.awaiting_approval is False
        assert list_details.published is True

    def test_cannot_request_approval(self, api_client, new_list_id):
        with pytest.raises(ApiException, match=self._already_awaiting_approval_error) as e:
            api_client.request_approval(new_list_id)
        assert e.value.status_code == 400


# TODO test lifecylce methods on revision
