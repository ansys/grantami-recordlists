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

from unittest.mock import Mock
from uuid import uuid4

from ansys.grantami.serverapi_openapi import GsaDatabasesInfo, GsaDatabaseStatus, GsaSlimDatabase
from ansys.openapi.common import ApiClient
import pytest

from ansys.grantami.recordlists import RecordListItem
from ansys.grantami.recordlists._connection import _ItemResolver


@pytest.fixture
def client():
    yield Mock(spec=ApiClient)


@pytest.fixture()
def item_resolver(client):
    resolver = _ItemResolver(client, False)
    yield resolver


def test_map_lists_dbs_with_identical_guids(item_resolver, monkeypatch, client):
    duplicate_guid = uuid4().hex
    database_api = item_resolver._db_schema_api
    monkeypatch.setattr(
        database_api,
        "get_all_databases",
        lambda: GsaDatabasesInfo(
            databases=[
                GsaSlimDatabase(
                    guid=duplicate_guid,
                    is_locked=False,
                    is_read_only=False,
                    key="DB_KEY_1",
                    name="DB_1",
                    status=GsaDatabaseStatus.OK,
                ),
                GsaSlimDatabase(
                    guid=duplicate_guid,
                    is_locked=False,
                    is_read_only=False,
                    key="DB_KEY_2",
                    name="DB_2",
                    status=GsaDatabaseStatus.OK,
                ),
            ]
        ),
    )
    db_map = item_resolver._get_db_map()
    assert duplicate_guid in db_map
    assert db_map[duplicate_guid] == ["DB_KEY_1", "DB_KEY_2"]


@pytest.fixture
def item_1():
    yield RecordListItem(
        "DB_GUID",
        "TABLE_GUID_1",
        "HISTORY_GUID_1",
    )


@pytest.fixture
def item_2():
    yield RecordListItem(
        "DB_GUID",
        "TABLE_GUID_2",
        "HISTORY_GUID_2",
    )


def test_items_are_resolved_in_all_dbs_with_matched_guid(
    item_resolver, monkeypatch, item_1, item_2
):
    monkeypatch.setattr(item_resolver, "_get_db_map", lambda: {"DB_GUID": ["DB_KEY_1", "DB_KEY_2"]})
    mock_resolve_item_in_db = Mock(return_value=False)
    monkeypatch.setattr(item_resolver, "_is_item_resolvable_in_db", mock_resolve_item_in_db)

    resolved_items = item_resolver.get_resolvable_items([item_1, item_2])
    assert mock_resolve_item_in_db.call_count == 4
    assert mock_resolve_item_in_db.call_args_list == [
        ((item_1, "DB_KEY_1"),),
        ((item_1, "DB_KEY_2"),),
        ((item_2, "DB_KEY_1"),),
        ((item_2, "DB_KEY_2"),),
    ]
    assert resolved_items == []


def test_resolver_exits_early_if_item_is_matched(item_resolver, item_1, monkeypatch):
    monkeypatch.setattr(item_resolver, "_get_db_map", lambda: {"DB_GUID": ["DB_KEY_1", "DB_KEY_2"]})
    mock_resolve_item_in_db = Mock(return_value=True)
    monkeypatch.setattr(item_resolver, "_is_item_resolvable_in_db", mock_resolve_item_in_db)

    resolved_items = item_resolver.get_resolvable_items([item_1])
    mock_resolve_item_in_db.assert_called_once_with(item_1, "DB_KEY_1")
    assert resolved_items == [item_1]
