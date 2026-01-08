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

examples_as_strings = {
    "test_get_all_lists": r"""{"lists":[{"identifier": "bffba6ef-b85a-4b26-932b-00875b74ca2e", "metadata": {}, "createdTimestamp": "2023-01-12T11:17:46.88+00:00", "createdUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "lastModifiedTimestamp": "2023-02-02T13:05:54.717+00:00", "lastModifiedUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "publishedTimestamp": "2023-01-27T14:36:29.967+00:00", "publishedUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "isRevision": false, "name": "Test List", "description": "Test List - Description", "notes": "Test List - Notes", "published": false, "awaitingApproval": false, "internalUse": false}, {"identifier": "5ca1d3f6-9afd-427c-ad09-03e2b71bfd75", "metadata": {}, "createdTimestamp": "2023-02-03T12:31:17.507+00:00", "createdUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "lastModifiedTimestamp": "2023-02-03T12:31:17.507+00:00", "lastModifiedUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "isRevision": false, "name": "CreateTest", "published": false, "awaitingApproval": false, "internalUse": false}]}""",  # noqa: E501
    "test_get_single_list": r"""{"identifier": "bffba6ef-b85a-4b26-932b-00875b74ca2e", "metadata": {}, "createdTimestamp": "2023-01-12T11:17:46.88+00:00", "createdUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "lastModifiedTimestamp": "2023-02-02T13:05:54.717+00:00", "lastModifiedUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "publishedTimestamp": "2023-01-27T14:36:29.967+00:00", "publishedUser": {"identifier": "7134b26c-42df-4e86-b801-317f05b8c399", "displayName": "DOMAIN\\mi_user", "name": "DOMAIN\\mi_user"}, "isRevision": false, "name": "Test List", "description": "Test List - Description", "notes": "Test List - Notes", "published": false, "awaitingApproval": false, "internalUse": false}""",  # noqa: E501
    "test_get_all_audit_log_entries": r"""[{"listIdentifier":"f235a25c-4deb-45cf-b6fd-c4fbaca3cbd0","initiatingUser":{"identifier":"7134b26c-42df-4e86-b801-317f05b8c399","displayName":"DOMAIN\\mi_user","name":"DOMAIN\\mi_user"},"action":"ListSetToAwaitingApprovalForWithdrawal","timestamp":"2025-01-08T11:15:18.1168375+00:00"},{"listIdentifier":"f235a25c-4deb-45cf-b6fd-c4fbaca3cbd0","initiatingUser":{"identifier":"7134b26c-42df-4e86-b801-317f05b8c399","displayName":"DOMAIN\\mi_user","name":"DOMAIN\\mi_user"},"action":"ListCreated","timestamp":"2025-01-08T11:15:17.8512115+00:00"}]""",
}
