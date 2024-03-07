from ansys.openapi.common import ApiException
import pytest

pytestmark = pytest.mark.integration


def test_create_list(basic_client, list_name):
    record_list = basic_client.create_list(name=list_name)

    assert record_list.name == list_name
    assert isinstance(record_list.identifier, str)


@pytest.fixture
def basic_list(basic_client, list_name, request):
    new_list = basic_client.create_list(name=list_name)
    cleanup = getattr(request, "param", {}).get("cleanup", True)
    yield new_list
    if cleanup:
        basic_client.delete_list(new_list)


class TestAuthoredListLifeCycle:
    """
    Check that even a user without elevated list permissions (curators, administrators) can perform
    some lifecycle operations on a list they themselves authored.

    Test methods cover two client methods each, to avoid proliferation of fixtures that would be
    required to get a list in the expected state.
    """

    def test_can_request_approval_but_not_publish(self, basic_client, basic_list):
        list_details = basic_client.request_list_approval(basic_list)
        assert list_details.awaiting_approval is True
        assert list_details.published is False

        with pytest.raises(ApiException) as e:
            basic_client.publish_list(basic_list)
        assert e.value.status_code == 403

    @pytest.fixture
    def basic_published_list_id(self, admin_client, basic_client, basic_list):
        basic_list = basic_client.request_list_approval(basic_list)
        basic_list = admin_client.publish_list(basic_list)
        yield basic_list

        # Need to withdraw the list, otherwise the current user cannot delete its own list
        admin_client.unpublish_list(basic_list)

    def test_can_request_withdrawal_but_not_withdraw(self, basic_client, basic_published_list_id):
        list_details = basic_client.request_list_approval(basic_published_list_id)
        assert list_details.awaiting_approval is True
        assert list_details.published is True

        with pytest.raises(ApiException) as e:
            basic_client.unpublish_list(basic_published_list_id)
        assert e.value.status_code == 403


class TestListLifeCycle:
    """
    Check that a user without elevated list permissions (curators, administrators) cannot perform
    lifecycle operations on a list they have not authored.
    """

    def test_all_stages(self, admin_client, basic_client, new_list):
        """Single test to avoid duplication."""
        # new_list_id is the identifier of a list created by the admin user

        with pytest.raises(ApiException) as e:
            basic_client.request_list_approval(new_list)
        assert e.value.status_code == 403

        admin_client.request_list_approval(new_list)
        with pytest.raises(ApiException) as e:
            basic_client.publish_list(new_list)
        assert e.value.status_code == 403

        admin_client.publish_list(new_list)
        with pytest.raises(ApiException) as e:
            basic_client.request_list_approval(new_list)
        assert e.value.status_code == 403

        admin_client.request_list_approval(new_list)
        with pytest.raises(ApiException) as e:
            basic_client.unpublish_list(new_list)
        assert e.value.status_code == 403


class TestSubscriptionLifeCycle:
    @pytest.fixture
    def published_list(self, admin_client, new_list):
        admin_client.request_list_approval(new_list)
        _published_list = admin_client.publish_list(new_list)
        return _published_list

    def test_cannot_subscribe_to_non_published_list(self, basic_client, new_list):
        with pytest.raises(ApiException) as e:
            basic_client.subscribe_to_list(new_list)
        assert e.value.status_code == 403

    def test_can_unsubscribe_from_non_subscribed_list(self, basic_client, new_list):
        basic_client.unsubscribe_from_list(new_list)

    def test_can_unsubscribe_from_non_subscribed_published_list(self, basic_client, published_list):
        basic_client.unsubscribe_from_list(published_list)

    def test_can_subscribe_then_unsubscribe_to_published_list(
        self, basic_client, published_list, list_username_no_permissions
    ):
        # Subscribe
        basic_client.subscribe_to_list(published_list)

        # Check as user with limited permissions, can only see its own permissions
        permissions = basic_client.list_permissions_api.get_permissions(
            list_identifier=published_list.identifier
        )
        assert len(permissions.user_permissions) == 1
        user_permissions = permissions.user_permissions[0]
        assert list_username_no_permissions in user_permissions.user_or_group_name
        assert user_permissions.flags.is_subscribed is True

        # Unsubscribe
        basic_client.unsubscribe_from_list(published_list)

        # Check
        permissions = basic_client.list_permissions_api.get_permissions(
            list_identifier=published_list.identifier
        )
        assert len(permissions.user_permissions) == 0
