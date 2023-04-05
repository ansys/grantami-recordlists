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
