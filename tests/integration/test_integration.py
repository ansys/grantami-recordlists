# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import uuid

from ansys.openapi.common import ApiException
import pytest

from ansys.grantami.recordlists import (
    BooleanCriterion,
    RecordList,
    RecordListItem,
    SearchCriterion,
    UserRole,
)

pytestmark = pytest.mark.integration


def test_getting_all_lists(admin_client, new_list):
    # Using new_list fixture to ensure there is at least one list when this test is run
    all_lists = admin_client.get_all_lists()
    assert isinstance(all_lists, list)
    assert all(isinstance(l, RecordList) for l in all_lists)
    my_list = next(rl for rl in all_lists if rl.identifier == new_list.identifier)


class TestListItems:
    def test_get_list_items_one_unresolvable_item(
        self,
        admin_client,
        new_list_with_one_unresolvable_item,
    ):
        record_list_items = admin_client.get_list_items(new_list_with_one_unresolvable_item)

        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == 1

    def test_get_list_items_many_unresolvable_items(
        self,
        admin_client,
        new_list_with_many_unresolvable_items,
        many_unresolvable_items,
    ):
        record_list_items = admin_client.get_list_items(new_list_with_many_unresolvable_items)

        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == len(many_unresolvable_items)

    def test_items_management(self, admin_client, new_list, unresolvable_item):
        another_item = RecordListItem(
            unresolvable_item.database_guid,
            unresolvable_item.table_guid,
            record_history_guid=str(uuid.uuid4()),
        )
        items = admin_client.add_items_to_list(new_list, items=[unresolvable_item])
        assert items == [unresolvable_item]

        items = admin_client.add_items_to_list(new_list, items=[another_item])
        assert unresolvable_item in items and another_item in items and len(items) == 2

        items = admin_client.remove_items_from_list(new_list, items=[unresolvable_item])
        assert items == [another_item]

        items = admin_client.remove_items_from_list(new_list, items=[another_item])
        assert items == []


class TestItemResolvability:
    """5 test cases

    [Admin user] x
    [One unresolv., Many unresolv., One resolv., Many resolv., Mixture]
    """

    def test_get_list_items_one_unresolvable_item(
        self,
        admin_client,
        new_list_with_one_unresolvable_item,
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_list_with_one_unresolvable_item
        )

        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == 0

    def test_get_list_items_many_unresolvable_items(
        self,
        admin_client,
        new_list_with_many_unresolvable_items,
        many_unresolvable_items,
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_list_with_many_unresolvable_items
        )

        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == 0

    def test_get_list_items_one_resolvable_item(
        self,
        admin_client,
        new_list_with_one_resolvable_item,
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_list_with_one_resolvable_item
        )

        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == 1

    def test_get_list_items_many_resolvable_items(
        self,
        admin_client,
        new_list_with_many_resolvable_items,
        resolvable_items,
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_list_with_many_resolvable_items
        )

        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == len(resolvable_items)

    def test_get_list_items_many_resolvable_and_unresolvable_items(
        self,
        admin_client,
        new_list_with_many_resolvable_and_unresolvable_items,
        resolvable_items,
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_list_with_many_resolvable_and_unresolvable_items
        )

        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == len(resolvable_items)


class TestItemResolvabilityVersionControl:
    """15 test cases

    [Admin user, Admin user read mode, Read user] x
    [Unreleased, Released, Draft superseded, Draft superseding, Superseded]
    """

    @staticmethod
    def check_resolved_record(record_list_items, record_version, record_guid_check: bool = True):
        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == 1
        assert record_list_items[0].record_version == record_version
        if record_guid_check:
            assert record_list_items[0].record_guid is not None

    @staticmethod
    def check_unresolved_record(record_list_items):
        assert isinstance(record_list_items, list)
        assert len(record_list_items) == 0

    def test_admin_user_can_resolve_unreleased_item(
        self, admin_client, new_admin_list_with_one_unreleased_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_unreleased_item
        )
        self.check_resolved_record(record_list_items, record_version=1, record_guid_check=False)

    def test_admin_user_can_resolve_released_item(
        self, admin_client, new_admin_list_with_one_released_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_released_item
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_admin_user_can_resolve_draft_superseded_item(
        self, admin_client, new_admin_list_with_one_draft_superseded_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseded_item
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_admin_user_can_resolve_draft_superseding_item(
        self, admin_client, new_admin_list_with_one_draft_superseding_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseding_item
        )
        self.check_resolved_record(record_list_items, record_version=2, record_guid_check=False)

    def test_admin_user_can_resolve_superseded_item(
        self, admin_client, new_admin_list_with_one_superseded_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_superseded_item
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_admin_user_read_mode_cannot_resolve_unreleased_item(
        self, admin_client, new_admin_list_with_one_unreleased_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_unreleased_item,
            read_mode=True,
        )
        self.check_unresolved_record(record_list_items)

    def test_admin_user_read_mode_can_resolve_released_item(
        self, admin_client, new_admin_list_with_one_released_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_released_item,
            read_mode=True,
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_admin_user_read_mode_can_resolve_draft_superseded_item(
        self, admin_client, new_admin_list_with_one_draft_superseded_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseded_item,
            read_mode=True,
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_admin_user_read_mode_cannot_resolve_draft_superseding_item(
        self, admin_client, new_admin_list_with_one_draft_superseding_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseding_item,
            read_mode=True,
        )
        self.check_unresolved_record(record_list_items)

    def test_admin_user_read_mode_can_resolve_superseded_item(
        self, admin_client, new_admin_list_with_one_superseded_item
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_superseded_item,
            read_mode=True,
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_read_user_cannot_resolve_unreleased_item(
        self, basic_client, new_basic_list_with_one_unreleased_item
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_unreleased_item
        )
        self.check_unresolved_record(record_list_items)

    def test_read_user_can_resolve_released_item(
        self, basic_client, new_basic_list_with_one_released_item
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_released_item
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_read_user_can_resolve_draft_superseded_item(
        self, basic_client, new_basic_list_with_one_draft_superseded_item
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_draft_superseded_item,
        )
        self.check_resolved_record(record_list_items, record_version=1)

    def test_read_user_cannot_resolve_draft_superseding_item(
        self, basic_client, new_basic_list_with_one_draft_superseding_item
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_draft_superseding_item
        )
        self.check_unresolved_record(record_list_items)

    def test_read_user_can_resolve_superseded_item(
        self, basic_client, new_basic_list_with_one_superseded_item
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_superseded_item
        )
        self.check_resolved_record(record_list_items, record_version=1)


class TestItemResolvabilityVersionControlByHistory:
    """15 test cases

    [Admin user, Admin user read mode, Read user] x
    [Unreleased, Released, Draft superseded, Draft superseding, Superseded]
    """

    @staticmethod
    def check_resolved_record(record_list_items):
        assert isinstance(record_list_items, list)
        assert all(isinstance(item, RecordListItem) for item in record_list_items)
        assert len(record_list_items) == 1
        assert record_list_items[0].record_guid is None
        assert record_list_items[0].record_version is None

    @staticmethod
    def check_unresolved_record(record_list_items):
        assert isinstance(record_list_items, list)
        assert len(record_list_items) == 0

    def test_admin_user_can_resolve_unreleased_item_by_history(
        self, admin_client, new_admin_list_with_one_unreleased_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_unreleased_item_by_history
        )
        self.check_resolved_record(record_list_items)

    def test_admin_user_can_resolve_released_item_by_history(
        self, admin_client, new_admin_list_with_one_released_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_released_item_by_history
        )
        self.check_resolved_record(record_list_items)

    def test_admin_user_can_resolve_draft_superseded_item_by_history(
        self, admin_client, new_admin_list_with_one_draft_superseded_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseded_item_by_history
        )
        self.check_resolved_record(record_list_items)

    def test_admin_user_can_resolve_draft_superseding_item_by_history(
        self, admin_client, new_admin_list_with_one_draft_superseding_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseding_item_by_history
        )
        self.check_resolved_record(record_list_items)

    def test_admin_user_can_resolve_superseded_item_by_history(
        self, admin_client, new_admin_list_with_one_superseded_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_superseded_item_by_history
        )
        self.check_resolved_record(record_list_items)

    def test_admin_user_read_mode_cannot_resolve_unreleased_item_by_history(
        self, admin_client, new_admin_list_with_one_unreleased_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_unreleased_item_by_history,
            read_mode=True,
        )
        self.check_unresolved_record(record_list_items)

    def test_admin_user_read_mode_can_resolve_released_item_by_history(
        self, admin_client, new_admin_list_with_one_released_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_released_item_by_history,
            read_mode=True,
        )
        self.check_resolved_record(record_list_items)

    def test_admin_user_read_mode_can_resolve_draft_superseded_item_by_history(
        self, admin_client, new_admin_list_with_one_draft_superseded_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseded_item_by_history,
            read_mode=True,
        )
        # Falls back to v1
        self.check_resolved_record(record_list_items)

    def test_admin_user_read_mode_cannot_resolve_draft_superseding_item_by_history(
        self, admin_client, new_admin_list_with_one_draft_superseding_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_draft_superseding_item_by_history,
            read_mode=True,
        )
        # Resolves v1
        self.check_resolved_record(record_list_items)

    def test_admin_user_read_mode_can_resolve_superseded_item_by_history(
        self, admin_client, new_admin_list_with_one_superseded_item_by_history
    ):
        record_list_items = admin_client.get_resolvable_list_items(
            new_admin_list_with_one_superseded_item_by_history,
            read_mode=True,
        )
        self.check_resolved_record(record_list_items)

    def test_read_user_cannot_resolve_unreleased_item_by_history(
        self, basic_client, new_basic_list_with_one_unreleased_item_by_history
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_unreleased_item_by_history,
        )
        self.check_unresolved_record(record_list_items)

    def test_read_user_can_resolve_released_item_by_history(
        self, basic_client, new_basic_list_with_one_released_item_by_history
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_released_item_by_history,
        )
        self.check_resolved_record(record_list_items)

    def test_read_user_can_resolve_draft_superseded_item_by_history(
        self, basic_client, new_basic_list_with_one_draft_superseded_item_by_history
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_draft_superseded_item_by_history,
        )
        # Falls back to v1
        self.check_resolved_record(record_list_items)

    def test_read_user_cannot_resolve_draft_superseding_item_by_history(
        self, basic_client, new_basic_list_with_one_draft_superseding_item_by_history
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_draft_superseding_item_by_history,
        )
        # Resolves v1
        self.check_resolved_record(record_list_items)

    def test_read_user_can_resolve_superseded_item_by_history(
        self, basic_client, new_basic_list_with_one_superseded_item_by_history
    ):
        record_list_items = basic_client.get_resolvable_list_items(
            new_basic_list_with_one_superseded_item_by_history,
        )
        self.check_resolved_record(record_list_items)


def test_create_minimal_list(admin_client, cleanup_admin, list_name):
    record_list = admin_client.create_list(name=list_name)
    cleanup_admin.append(record_list)

    assert record_list.name == list_name
    assert record_list.notes is None
    assert record_list.description is None
    assert isinstance(record_list.identifier, str)


@pytest.mark.parametrize("new_list", [{"cleanup": False}], indirect=True)
def test_delete_list(admin_client, new_list, list_name):
    admin_client.delete_list(new_list)

    with pytest.raises(ApiException) as exc:
        my_list = admin_client.get_list(new_list.identifier)
    assert exc.value.status_code == 404


def test_update_list(admin_client, new_list):
    admin_client.update_list(new_list, name="NEWUPDATEDNAME")
    record_list = admin_client.get_list(new_list.identifier)
    assert record_list.name == "NEWUPDATEDNAME"


def test_update_list_nullable_property(admin_client, new_list):
    admin_client.update_list(new_list, notes="Some notes")
    record_list = admin_client.get_list(new_list.identifier)
    assert record_list.notes == "Some notes"

    admin_client.update_list(new_list, notes=None)
    record_list = admin_client.get_list(new_list.identifier)
    assert record_list.notes is None


def test_copy_list(admin_client, cleanup_admin, new_list):
    list_copy = admin_client.copy_list(new_list)
    cleanup_admin.append(list_copy)
    assert list_copy.identifier != new_list

    original_list = new_list

    # Copied list name is original list name + " copy_{timestamp}"
    assert original_list.name in list_copy.name
    assert list_copy.description == original_list.description
    assert list_copy.notes == original_list.notes


def test_revise_unpublished_list(admin_client, new_list):
    with pytest.raises(ApiException) as exc:
        admin_client.revise_list(new_list)

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
    created_list = create_client.create_list(name=list_name)
    cleanup.append(created_list)

    with pytest.raises(ApiException) as e:
        read_client.get_list(created_list.identifier)
    assert e.value.status_code == 403


class TestLifeCycle:
    _not_awaiting_approval_error = "The list is not currently awaiting approval."
    _already_awaiting_approval_error = "The list is already awaiting approval."


class TestLifeCycleNewList(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = False, published = False
    """

    def test_cannot_publish(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.publish_list(new_list)
        assert e.value.status_code == 400

    def test_cannot_withdraw(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.unpublish_list(new_list)
        assert e.value.status_code == 400

    def test_cannot_reset(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.cancel_list_approval_request(new_list)
        assert e.value.status_code == 400

    def test_can_request_approval(self, admin_client, new_list):
        list_details = admin_client.request_list_approval(new_list)
        assert list_details.awaiting_approval is True


class TestLifeCycleAwaitingApprovalAndNotPublished(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = True, published = False
    """

    @pytest.fixture(autouse=True)
    def request_approval_for_list(self, admin_client, new_list):
        admin_client.request_list_approval(new_list)

    def test_can_publish(self, admin_client, new_list):
        list_details = admin_client.publish_list(new_list)
        assert list_details.awaiting_approval is False
        assert list_details.published is True
        assert list_details.published_timestamp is not None
        assert list_details.published_user is not None

    def test_cannot_withdraw(self, admin_client, new_list):
        with pytest.raises(ApiException, match="not currently published") as e:
            admin_client.unpublish_list(new_list)
        assert e.value.status_code == 400

    def test_can_reset(self, admin_client, new_list):
        list_details = admin_client.cancel_list_approval_request(new_list)
        assert list_details.awaiting_approval is False

    def test_cannot_request_approval(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._already_awaiting_approval_error) as e:
            admin_client.request_list_approval(new_list)
        assert e.value.status_code == 400


class TestLifeCyclePublishedAndNotAwaitingApproval(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = False, published = True
    """

    @pytest.fixture(autouse=True)
    def publish_list(self, admin_client, new_list):
        admin_client.request_list_approval(new_list)
        admin_client.publish_list(new_list)

    def test_cannot_publish(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.publish_list(new_list)
        assert e.value.status_code == 400

    def test_cannot_withdraw(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.unpublish_list(new_list)
        assert e.value.status_code == 400

    def test_cannot_reset(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._not_awaiting_approval_error) as e:
            admin_client.cancel_list_approval_request(new_list)
        assert e.value.status_code == 400

    def test_cannot_request_approval(self, admin_client, new_list):
        list_details = admin_client.request_list_approval(new_list)
        assert list_details.awaiting_approval is True
        assert list_details.published is True


class TestRevisionLifeCycle(TestLifeCyclePublishedAndNotAwaitingApproval):
    # Inherits the auto-use fixture to publish the list

    def test_revise_published_list(self, admin_client, new_list):
        list_details = admin_client.revise_list(new_list)
        assert list_details.published is False
        assert list_details.awaiting_approval is False
        assert list_details.parent_record_list_identifier == new_list.identifier

        updated_note = "Notes added to list revision"
        _ = admin_client.update_list(list_details, notes=updated_note)

        updated_list = admin_client.request_list_approval(list_details)
        returned_list = admin_client.publish_list(list_details)

        with pytest.raises(ApiException) as e:
            revision_list_details = admin_client.get_list(list_details.identifier)
        assert e.value.status_code == 404

        original_list_details = admin_client.get_list(new_list.identifier)
        assert original_list_details.notes == updated_note

    def test_cannot_edit_properties_of_published_list(self, admin_client, new_list):
        with pytest.raises(ApiException) as e:
            admin_client.update_list(new_list, description="Updated description")
        assert e.value.status_code == 403

    def test_cannot_edit_items_of_published_list(self, admin_client, new_list, unresolvable_item):
        with pytest.raises(ApiException) as e:
            admin_client.add_items_to_list(
                new_list,
                items=[unresolvable_item],
            )
        assert e.value.status_code == 403


class TestLifeCyclePublishedAndAwaitingApproval(TestLifeCycle):
    """
    Test workflow methods for RecordList with awaiting_approval = True, published = True
    """

    @pytest.fixture(autouse=True)
    def publish_and_request_approval_for_list(self, admin_client, new_list):
        # TODO refactor if we allow creating lists with predefined statuses
        admin_client.request_list_approval(new_list)
        admin_client.publish_list(new_list)
        admin_client.request_list_approval(new_list)

    def test_cannot_publish(self, admin_client, new_list):
        with pytest.raises(ApiException, match="already published") as e:
            admin_client.publish_list(new_list)
        assert e.value.status_code == 400

    def test_can_withdraw(self, admin_client, new_list):
        list_details = admin_client.unpublish_list(new_list)
        assert list_details.published is False
        assert list_details.awaiting_approval is False

    def test_can_reset(self, admin_client, new_list):
        list_details = admin_client.cancel_list_approval_request(new_list)
        assert list_details.awaiting_approval is False
        assert list_details.published is True

    def test_cannot_request_approval(self, admin_client, new_list):
        with pytest.raises(ApiException, match=self._already_awaiting_approval_error) as e:
            admin_client.request_list_approval(new_list)
        assert e.value.status_code == 400


class TestSearch:
    """Exercises some search criteria."""

    _name_suffix_A = "_ListA"
    _name_suffix_B = "_ListB"
    _name_suffix_C = "_ListC"

    @pytest.fixture(scope="class")
    def list_a(self, admin_client, list_name):
        """A personal list with a known name."""
        created_list = admin_client.create_list(list_name + self._name_suffix_A)
        yield created_list
        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class")
    def list_b(self, admin_client, list_name):
        """A published list with a known name."""
        created_list = admin_client.create_list(list_name + self._name_suffix_B)
        admin_client.request_list_approval(created_list)
        admin_client.publish_list(created_list)
        yield created_list
        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class")
    def list_c(self, admin_client, list_name, list_b, two_resolvable_items_in_table):
        """A revision of list B with a known name and items."""
        created_list = admin_client.revise_list(list_b)
        admin_client.update_list(created_list, name=list_name + self._name_suffix_C)
        admin_client.add_items_to_list(created_list, two_resolvable_items_in_table)
        yield created_list
        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class", autouse=True)
    def multiple_lists(self, list_a, list_b, list_c):
        yield list_a, list_b, list_c

    def test_search_list_name_match_all(self, admin_client, list_name):
        # All tests include name_contains=list_name to filter results to lists created in this test
        #  session.
        criteria = SearchCriterion(name_contains=list_name)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 3

    def test_search_list_name_match_one(self, admin_client, list_a):
        criteria = SearchCriterion(name_contains=self._name_suffix_A)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_a.identifier

    def test_search_not_published_or_awaiting(self, admin_client, list_a):
        criteria = SearchCriterion(
            name_contains=self._name_suffix_A,
            is_published=False,
            is_awaiting_approval=False,
            is_revision=False,
            is_internal_use=False,
        )
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_a.identifier

    def test_search_published(self, admin_client, list_name, list_b):
        criteria = SearchCriterion(name_contains=list_name, is_published=True)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_b.identifier

    def test_search_revision(self, admin_client, list_name, list_c):
        criteria = SearchCriterion(name_contains=list_name, is_revision=True)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_c.identifier

    @pytest.mark.parametrize("include_items", [True, False])
    def test_search_by_database(
        self,
        include_items,
        admin_client,
        list_name,
        two_resolvable_items_in_table,
        list_c,
        training_database_guid,
    ):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_databases=[training_database_guid],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)
        assert len(results) == 2
        for result in results:
            assert result.record_list.identifier == list_c.identifier
            if include_items:
                assert len(result.items) == 2
            else:
                assert result.items is None

    @pytest.mark.parametrize("include_items", [True, False])
    def test_search_by_multiple_databases(
        self,
        include_items,
        admin_client,
        list_name,
        two_resolvable_items_in_table,
        list_c,
        training_database_guid,
    ):
        # List of databases = Is in one OR the other
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_databases=[training_database_guid, str(uuid.uuid4())],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)
        assert len(results) == 2
        for result in results:
            assert result.record_list.identifier == list_c.identifier
            if include_items:
                assert len(result.items) == 2
            else:
                assert result.items is None

    @pytest.mark.parametrize("include_items", [True, False])
    def test_search_by_table(
        self,
        include_items,
        admin_client,
        list_name,
        two_resolvable_items_in_table,
        list_c,
        design_data_table_guid,
    ):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_tables=[design_data_table_guid],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)
        assert len(results) == 2
        for result in results:
            assert result.record_list.identifier == list_c.identifier
            if include_items:
                assert len(result.items) == 2
            else:
                assert result.items is None

    @pytest.mark.parametrize("include_items", [True, False])
    def test_search_by_record(
        self, include_items, admin_client, list_name, two_resolvable_items_in_table, list_c
    ):
        record_history_guid = two_resolvable_items_in_table[0].record_history_guid
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records=[record_history_guid],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_c.identifier
        if include_items:
            assert len(results[0].items) == 1
        else:
            assert results[0].items is None

    def test_search_role_is_none(self, admin_client, list_name):
        criteria = SearchCriterion(user_role=UserRole.NONE)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 0

    def test_search_role_is_owner(self, admin_client, list_name):
        criteria = SearchCriterion(name_contains=list_name, user_role=UserRole.OWNER)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 3

    def test_match_all(self, admin_client, list_name, new_list, list_a):
        # Uses fixture new_list to create a list with the root name only and assert that the
        # match_all criteria is excluding it as expected.
        criteria = BooleanCriterion(
            match_all=[
                SearchCriterion(name_contains=list_name),
                SearchCriterion(name_contains=self._name_suffix_A),
            ]
        )
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_a.identifier

    def test_nested_boolean_criteria(self, admin_client, list_name, new_list, list_a, list_b):
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
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 2
        ids = {result.record_list.identifier for result in results}
        assert list_a.identifier in ids
        assert list_b.identifier in ids

    def test_boolean_match_any_and_all(
        self,
        admin_client,
        list_name,
        list_a,
        list_b,
    ):
        criteria = BooleanCriterion(
            match_any=[
                SearchCriterion(name_contains=self._name_suffix_A),
                SearchCriterion(name_contains=self._name_suffix_B),
            ],
            match_all=[SearchCriterion(name_contains=list_name)],
        )
        results = admin_client.search_for_lists(criteria)
        ids = {result.record_list.identifier for result in results}
        assert {list_a.identifier, list_b.identifier} == ids

    def test_include_items_flag(self, admin_client, list_c, two_resolvable_items_in_table):
        results = admin_client.search_for_lists(
            SearchCriterion(name_contains=self._name_suffix_C),
            include_items=True,
        )
        assert len(results) == 1
        result = results[0]
        assert result.record_list.identifier == list_c.identifier
        # Check the result does have the expected items
        check_count = 0
        for result_item in result.items:
            for input_item in two_resolvable_items_in_table:
                if result_item.record_history_guid == input_item.record_history_guid:
                    assert result_item.database_guid == input_item.database_guid
                    assert result_item.table_guid == input_item.table_guid
                    assert result_item.record_guid == input_item.record_guid
                    assert result_item.record_version == input_item.record_version
                    check_count += 1
        assert check_count == len(result.items) == len(two_resolvable_items_in_table)
