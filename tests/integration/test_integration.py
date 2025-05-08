# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from datetime import datetime
from enum import Enum
import uuid

from ansys.openapi.common import ApiException
import pytest

from ansys.grantami.recordlists import (
    AuditLogAction,
    AuditLogSearchCriterion,
    BooleanCriterion,
    Connection,
    RecordList,
    RecordListItem,
    RecordListsApiClient,
    SearchCriterion,
    SearchResult,
    UserOrGroup,
    UserRole,
)
from ansys.grantami.recordlists._connection import RecordLists2025R12024R2ApiClient

pytestmark = pytest.mark.integration(mi_versions=[(25, 2), (25, 1), (24, 2)])


class TestConnection:
    @pytest.mark.integration(mi_versions=[(25, 2)])
    def test_latest_mi_version(self, sl_url, list_admin_username, list_admin_password):
        connection = Connection(sl_url).with_credentials(list_admin_username, list_admin_password)
        client = connection.connect()
        assert isinstance(client, RecordListsApiClient)
        assert not isinstance(client, RecordLists2025R12024R2ApiClient)

    @pytest.mark.integration(mi_versions=[(25, 1), (24, 2)])
    def test_older_supported_mi_version(self, sl_url, list_admin_username, list_admin_password):
        connection = Connection(sl_url).with_credentials(list_admin_username, list_admin_password)
        client = connection.connect()
        assert isinstance(client, RecordListsApiClient)
        assert isinstance(client, RecordLists2025R12024R2ApiClient)

    @pytest.mark.integration(mi_versions=[(24, 1)])
    def test_unsupported_mi_version(self, sl_url, list_admin_username, list_admin_password):
        # We don't raise the expected version-specific error message because the Server API location has moved since
        # 2024 R1 was released.
        connection = Connection(sl_url).with_credentials(list_admin_username, list_admin_password)
        with pytest.raises(
            ConnectionError,
            match=r"Cannot find the Server API definition in Granta MI Service Layer",
        ):
            connection.connect()


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

    @pytest.mark.parametrize("include_table_guid_for_deletion", [True, False])
    def test_items_management(
        self, admin_client, new_list, unresolvable_item, include_table_guid_for_deletion
    ):
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

        if include_table_guid_for_deletion is False:
            another_item = RecordListItem(
                database_guid=another_item.database_guid,
                table_guid=None,
                record_history_guid=another_item.record_history_guid,
            )
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


class _TestSearch:
    """Exercises some search criteria."""

    _name_suffix_personal = "_ListA"
    _name_suffix_published = "_ListB"
    _name_suffix_published_training_items = "_ListC"
    _name_suffix_rs_items = "_ListD"
    _name_suffix_training_and_rs_items = "_ListE"

    @pytest.fixture(scope="class")
    def list_personal(self, admin_client, list_name):
        """A personal list with a known name."""
        unique_list_name = f"{list_name}{self._name_suffix_personal}"
        created_list = admin_client.create_list(unique_list_name)

        yield created_list

        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class")
    def list_published(self, admin_client, list_name):
        """A published list with a known name."""
        unique_list_name = f"{list_name}{self._name_suffix_published}"
        created_list = admin_client.create_list(unique_list_name)
        admin_client.request_list_approval(created_list)
        admin_client.publish_list(created_list)

        yield created_list

        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class")
    def list_mi_training_items(self, admin_client, list_name, list_published, resolvable_items):
        """A revision of list B with a known name and items from MI Training."""
        created_list = admin_client.revise_list(list_published)
        unique_list_name = f"{list_name}{self._name_suffix_published_training_items}"
        admin_client.update_list(created_list, name=unique_list_name)
        admin_client.add_items_to_list(created_list, resolvable_items)

        yield created_list

        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class")
    def list_rs_items(self, admin_client, list_name, list_published, resolvable_rs_items):
        """A list with a known name and items from Restricted Substances."""
        unique_list_name = f"{list_name}{self._name_suffix_rs_items}"
        created_list = admin_client.create_list(unique_list_name)
        admin_client.add_items_to_list(created_list, resolvable_rs_items)

        yield created_list

        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class")
    def list_mi_training_and_rs_items(
        self, admin_client, list_name, list_published, resolvable_items, resolvable_rs_items
    ):
        """A list with a known name and items from MI Training and Restricted Substances."""
        unique_list_name = f"{list_name}{self._name_suffix_training_and_rs_items}"
        created_list = admin_client.create_list(unique_list_name)
        admin_client.add_items_to_list(created_list, resolvable_items)
        admin_client.add_items_to_list(created_list, resolvable_rs_items)

        yield created_list

        admin_client.delete_list(created_list)

    @pytest.fixture(scope="class", autouse=True)
    def multiple_lists(
        self,
        list_personal,
        list_published,
        list_mi_training_items,
        list_rs_items,
        list_mi_training_and_rs_items,
    ):
        """Forces all fixtures to execute at class instantiation."""
        yield list_personal, list_published, list_mi_training_items, list_rs_items, list_mi_training_and_rs_items

    def validate_list(
        self,
        search_results: list[SearchResult],
        list_suffix: str,
        items: list[RecordListItem] | None = None,
    ):
        result = next(r for r in search_results if r.record_list.name.endswith(list_suffix))
        if items is not None:
            assert len(result.items) == len(items)
        else:
            assert result.items is None


class TestSearchResult(_TestSearch):
    _properties_to_check = [
        "record_history_guid",
        "database_guid",
        "table_guid",
        "record_guid",
        "record_version",
    ]

    def test_search_result_contains_correct_items_single_database(
        self, admin_client, list_mi_training_items, resolvable_items
    ):
        results = admin_client.search_for_lists(
            SearchCriterion(name_contains=self._name_suffix_published_training_items),
            include_items=True,
        )

        assert len(results) == 1
        result = results[0]

        assert result.record_list.identifier == list_mi_training_items.identifier

        results = {
            tuple(getattr(item, prop) for prop in self._properties_to_check)
            for item in result.items
        }
        expected = {
            tuple(getattr(item, prop) for prop in self._properties_to_check)
            for item in resolvable_items
        }
        assert results == expected

    def test_search_result_contains_correct_items_multiple_databases(
        self, admin_client, list_mi_training_and_rs_items, resolvable_items, resolvable_rs_items
    ):
        results = admin_client.search_for_lists(
            SearchCriterion(name_contains=self._name_suffix_training_and_rs_items),
            include_items=True,
        )
        assert len(results) == 1
        result = results[0]
        assert result.record_list.identifier == list_mi_training_and_rs_items.identifier

        results = {
            tuple(getattr(item, prop) for prop in self._properties_to_check)
            for item in result.items
        }
        expected = {
            tuple(getattr(item, prop) for prop in self._properties_to_check)
            for item in resolvable_items + resolvable_rs_items
        }
        assert results == expected


class TestSearchByName(_TestSearch):
    def test_search_list_name_match_all(self, admin_client, list_name):
        # All tests include name_contains=list_name to filter results to lists created in this test
        #  session.
        criteria = SearchCriterion(name_contains=list_name)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 5

    def test_search_list_name_match_one(self, admin_client, list_personal):
        criteria = SearchCriterion(name_contains=self._name_suffix_personal)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_personal.identifier


class TestSearchByState(_TestSearch):
    def test_search_not_published_or_awaiting(self, admin_client, list_personal):
        criteria = SearchCriterion(
            name_contains=self._name_suffix_personal,
            is_published=False,
            is_awaiting_approval=False,
            is_revision=False,
            is_internal_use=False,
        )
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_personal.identifier

    def test_search_published(self, admin_client, list_name, list_published):
        criteria = SearchCriterion(name_contains=list_name, is_published=True)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_published.identifier

    def test_search_revision(self, admin_client, list_name, list_mi_training_items):
        criteria = SearchCriterion(name_contains=list_name, is_revision=True)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_mi_training_items.identifier


@pytest.mark.parametrize("include_items", [True, False])
class TestSearchByDatabase(_TestSearch):
    def test_single_database_two_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_items,
        resolvable_rs_items,
        list_mi_training_items,
        training_database_guid,
    ):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_databases=[training_database_guid],
        )

        results = admin_client.search_for_lists(criteria, include_items=include_items)

        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 2
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )

    def test_two_databases_two_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_items,
        resolvable_rs_items,
        list_mi_training_items,
        training_database_guid,
    ):
        # List of databases = Is in one OR the other
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_databases=[training_database_guid, str(uuid.uuid4())],
        )

        results = admin_client.search_for_lists(criteria, include_items=include_items)

        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 2
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )

    def test_two_databases_three_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_items,
        resolvable_rs_items,
        list_mi_training_items,
        training_database_guid,
        rs_database_guid,
    ):
        # List of databases = Is in one OR the other
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_databases=[training_database_guid, rs_database_guid],
        )

        results = admin_client.search_for_lists(criteria, include_items=include_items)

        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_rs_items: resolvable_rs_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 3
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )


@pytest.mark.parametrize("include_items", [True, False])
class TestSearchByTable(_TestSearch):
    def test_single_table_two_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_items,
        resolvable_rs_items,
        list_mi_training_items,
        design_data_table_guid,
    ):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_tables=[design_data_table_guid],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)

        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 2
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )

    def test_two_tables_two_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_items,
        resolvable_rs_items,
        list_mi_training_items,
        design_data_table_guid,
        tensile_statistical_data_table_guid,
    ):
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records_in_tables=[
                design_data_table_guid,
                tensile_statistical_data_table_guid,
            ],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)

        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 2
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )


@pytest.mark.parametrize(
    "resolvable_item_fixture_name", ["resolvable_items", "resolvable_items_without_table_guids"]
)
@pytest.mark.parametrize("include_items", [True, False])
class TestSearchByRecord(_TestSearch):
    def test_single_record_two_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_item_fixture_name,
        request,
        resolvable_rs_items,
        list_mi_training_items,
    ):
        resolvable_items = request.getfixturevalue(resolvable_item_fixture_name)
        record_reference = resolvable_items[0]
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records=[record_reference],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)
        assert len(results) == 2
        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 2
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )

    def test_two_records_same_database_two_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_item_fixture_name,
        request,
        resolvable_rs_items,
        list_mi_training_items,
    ):
        resolvable_items = request.getfixturevalue(resolvable_item_fixture_name)
        record_reference_1 = resolvable_items[0]
        record_reference_2 = resolvable_items[1]

        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records=[record_reference_1, record_reference_2],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)
        assert len(results) == 2
        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 2
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )

    @pytest.mark.integration(mi_versions=[(25, 2)])
    def test_two_records_different_databases_three_hits(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_item_fixture_name,
        request,
        resolvable_rs_items,
        list_mi_training_items,
    ):
        resolvable_items = request.getfixturevalue(resolvable_item_fixture_name)
        training_record_reference = resolvable_items[0]
        rs_record_reference = resolvable_rs_items[0]
        criteria = SearchCriterion(
            name_contains=list_name,
            contains_records=[training_record_reference, rs_record_reference],
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)

        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_rs_items: resolvable_rs_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 3
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )

    @pytest.mark.integration(mi_versions=[(25, 1), (24, 2)])
    def test_two_records_different_databases_three_hits_2025_r1(
        self,
        include_items,
        admin_client,
        list_name,
        resolvable_item_fixture_name,
        request,
        resolvable_rs_items,
        list_mi_training_items,
    ):
        resolvable_items = request.getfixturevalue(resolvable_item_fixture_name)
        training_record_reference = resolvable_items[0]
        rs_record_reference = resolvable_rs_items[0]
        criteria = BooleanCriterion(
            match_any=[
                SearchCriterion(
                    name_contains=list_name,
                    contains_records=[training_record_reference],
                ),
                SearchCriterion(
                    name_contains=list_name,
                    contains_records=[rs_record_reference],
                ),
            ]
        )
        results = admin_client.search_for_lists(criteria, include_items=include_items)

        expected_results = {
            self._name_suffix_published_training_items: resolvable_items,
            self._name_suffix_rs_items: resolvable_rs_items,
            self._name_suffix_training_and_rs_items: resolvable_rs_items + resolvable_items,
        }
        assert len(results) == 3
        for suffix, items in expected_results.items():
            self.validate_list(
                search_results=results,
                list_suffix=suffix,
                items=items if include_items else None,
            )


class TestSearchByUserRole(_TestSearch):
    def test_role_is_none(self, admin_client, list_name):
        criteria = SearchCriterion(user_role=UserRole.NONE)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 0

    def test_role_is_owner(self, admin_client, list_name):
        criteria = SearchCriterion(name_contains=list_name, user_role=UserRole.OWNER)
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 5


class TestBooleanSearch(_TestSearch):
    def test_match_all(self, admin_client, list_name, new_list, list_personal):
        # Uses fixture new_list to create a list with the root name only and assert that the
        # match_all criteria is excluding it as expected.
        criteria = BooleanCriterion(
            match_all=[
                SearchCriterion(name_contains=list_name),
                SearchCriterion(name_contains=self._name_suffix_personal),
            ]
        )
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 1
        assert results[0].record_list.identifier == list_personal.identifier

    def test_nested_boolean_criteria(
        self, admin_client, list_name, new_list, list_personal, list_published
    ):
        criteria = BooleanCriterion(
            match_any=[
                # Should match personal only
                BooleanCriterion(
                    match_all=[
                        SearchCriterion(name_contains=list_name),
                        SearchCriterion(name_contains=self._name_suffix_personal),
                    ]
                ),
                # Should match published only
                BooleanCriterion(
                    match_all=[
                        SearchCriterion(name_contains=list_name),
                        SearchCriterion(name_contains=self._name_suffix_published),
                        SearchCriterion(is_published=True),
                    ]
                ),
            ]
        )
        results = admin_client.search_for_lists(criteria)
        assert len(results) == 2
        ids = {result.record_list.identifier for result in results}
        assert list_personal.identifier in ids
        assert list_published.identifier in ids

    def test_boolean_match_any_and_all(
        self,
        admin_client,
        list_name,
        list_personal,
        list_published,
    ):
        criteria = BooleanCriterion(
            match_any=[
                SearchCriterion(name_contains=self._name_suffix_personal),
                SearchCriterion(name_contains=self._name_suffix_published),
            ],
            match_all=[SearchCriterion(name_contains=list_name)],
        )
        results = admin_client.search_for_lists(criteria)
        ids = {result.record_list.identifier for result in results}
        assert {list_personal.identifier, list_published.identifier} == ids


@pytest.mark.integration(mi_versions=[(25, 2)])
class TestAuditLogging:
    _name_suffix_A = "_ListA"
    _name_suffix_B = "_ListB"

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
        requested_list = admin_client.request_list_approval(created_list)
        published_list = admin_client.publish_list(requested_list)
        yield published_list
        requested_list = admin_client.request_list_approval(published_list)
        unpublished_list = admin_client.unpublish_list(requested_list)
        admin_client.delete_list(unpublished_list)

    @pytest.mark.skip(reason="Current performance and network issues with getting all lists")
    def test_get_all_log_entries(self, admin_client, list_a, list_b):
        log_entries = admin_client.get_all_audit_log_entries(page_size=100)
        for result in log_entries:
            assert isinstance(result.action, Enum)
            assert isinstance(result.list_identifier, str)
            _ = uuid.UUID(result.list_identifier)
            assert isinstance(result.timestamp, datetime)
            assert isinstance(result.initiating_user, UserOrGroup)
            _ = uuid.UUID(result.initiating_user.identifier)

    @pytest.mark.parametrize("paged", (True, False))
    def test_filter_log_entries_by_list(self, admin_client, list_a, list_b, paged):
        criterion = AuditLogSearchCriterion(filter_record_lists=[list_a.identifier])
        if paged:
            page_size = 100
        else:
            page_size = None
        results = list(admin_client.search_for_audit_log_entries(criterion, page_size=page_size))
        assert len(results) == 1
        assert results[0].list_identifier == list_a.identifier
        assert results[0].action == AuditLogAction.LISTCREATED

    def test_filter_log_entries_by_list_is_ordered(self, admin_client, list_a, list_b):
        criterion = AuditLogSearchCriterion(filter_record_lists=[list_b.identifier])
        results = list(admin_client.search_for_audit_log_entries(criterion))
        assert len(results) == 3
        for event in results:
            assert event.list_identifier == list_b.identifier
        expected_actions = [
            AuditLogAction.LISTPUBLISHED,
            AuditLogAction.LISTSETTOAWAITINGAPPROVALFORPUBLISHING,
            AuditLogAction.LISTCREATED,
        ]
        for event, action in zip(results, expected_actions):
            assert event.action == action
