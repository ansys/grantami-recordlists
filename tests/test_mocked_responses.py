# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
import json
import uuid

from requests_mock import ANY

from ansys.grantami.recordlists import AuditLogAction
from inputs.examples import examples_as_strings


def test_get_all_lists(mock_client, mocker, mock_response):
    with mocker:
        mocker.get(ANY, status_code=200, json=mock_response)
        response = mock_client.get_all_lists()

    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].name == "Test List"
    assert response[1].name == "CreateTest"


def test_get_single_list(mock_client, mocker, mock_response):
    with mocker:
        mocker.get(ANY, status_code=200, json=mock_response)
        response = mock_client.get_list("bffba6ef-b85a-4b26-932b-00875b74ca2e")

    assert response.name == "Test List"


def test_get_all_audit_log_entries_paged(api_url, mock_client, mocker):
    with mocker:
        response_id = "766b96c2-9b91-4625-a271-46b1da89eb55"
        response = {"searchResultIdentifier": f"{response_id}"}
        empty_response_id = str(uuid.uuid4())
        empty_response = {"searchResultIdentifier": f"{empty_response_id}"}
        mocker.post(
            f"{api_url}/proxy/v1.svc/mi/api/v1/lists/audit/search",
            [{"status_code": 201, "json": response}, {"status_code": 201, "json": empty_response}],
        )
        mocker.get(
            f"{api_url}/proxy/v1.svc/mi/api/v1/lists/audit/search/results/{response_id}",
            status_code=200,
            json=json.loads(examples_as_strings["test_get_all_audit_log_entries"]),
        )
        mocker.get(
            f"{api_url}/proxy/v1.svc/mi/api/v1/lists/audit/search/results/{empty_response_id}",
            status_code=200,
            json=[],
        )

        log_entries = list(mock_client.get_all_audit_log_entries())

        assert len(log_entries) == 2
        assert log_entries[1].list_identifier == "f235a25c-4deb-45cf-b6fd-c4fbaca3cbd0"
        assert log_entries[1].action == AuditLogAction.LISTCREATED
        assert log_entries[0].list_identifier == "f235a25c-4deb-45cf-b6fd-c4fbaca3cbd0"
        assert log_entries[0].action == AuditLogAction.LISTSETTOAWAITINGAPPROVALFORWITHDRAWAL


def test_get_all_audit_log_entries_not_paged(api_url, mock_client, mocker):
    with mocker:
        response_id = "766b96c2-9b91-4625-a271-46b1da89eb55"
        response = {"searchResultIdentifier": f"{response_id}"}

        mocker.post(
            f"{api_url}/proxy/v1.svc/mi/api/v1/lists/audit/search", status_code=201, json=response
        )
        mocker.get(
            f"{api_url}/proxy/v1.svc/mi/api/v1/lists/audit/search/results/{response_id}",
            status_code=200,
            json=json.loads(examples_as_strings["test_get_all_audit_log_entries"]),
        )

        log_entries = list(mock_client.get_all_audit_log_entries(page_size=None))

        assert len(log_entries) == 2
        assert log_entries[1].list_identifier == "f235a25c-4deb-45cf-b6fd-c4fbaca3cbd0"
        assert log_entries[1].action == AuditLogAction.LISTCREATED
        assert log_entries[0].list_identifier == "f235a25c-4deb-45cf-b6fd-c4fbaca3cbd0"
        assert log_entries[0].action == AuditLogAction.LISTSETTOAWAITINGAPPROVALFORWITHDRAWAL
