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

from typing import Optional

from ansys.grantami.serverapi_openapi.api import (
    RecordsRecordHistoriesApi,
    RecordsRecordVersionsApi,
    SchemaDatabasesApi,
    SchemaTablesApi,
    SearchApi,
)
from ansys.grantami.serverapi_openapi.models import (
    GsaCreateRecordHistory,
    GsaRecordPropertyCriterion,
    GsaRecordType,
    GsaSearchableRecordProperty,
    GsaSearchRequest,
    GsaShortTextDatumCriterion,
    GsaVersionState,
)
from ansys.openapi.common import ApiClient

DB_KEY = "MI_Training"
TABLE_NAME = "Design Data"


class VersionControlError(Exception):
    def __init__(
        self,
        history_name,
        required_version_number,
        required_version_state,
        current_version_number,
        current_version_state,
    ):
        message = (
            f"Cannot satisfy required record version for this record history. "
            f"'{history_name}' is currently v{current_version_number}: {current_version_state}, but "
            f"v{required_version_number}: {required_version_state} was requested."
        )
        super().__init__(message)


class RecordCreator:
    """Ensures a record version exists at the specified version number and state for a given
    record history.

    All histories are created by name in the root of the provided table. If the history does
    not exist, it will be created.

    Only certain combinations of state and version are supported.

    Parameters
    ----------
    admin_client : ApiClient
        Client to use for Server API record history and record version operations
    database_key : str
        Database in which to create/access record histories
    table_name : str
        Table name in which to create/access record histories
    history_name : str
        Name of the record to create/access
    """

    def __init__(
        self,
        admin_client: ApiClient,
        database_key: str,
        table_name: str,
        history_name: str,
    ):
        self.admin_client = admin_client
        self.database_key = database_key
        self.table_name = table_name
        self.history_name = history_name

        tables_api = SchemaTablesApi(self.admin_client)
        all_tables = tables_api.get_tables(database_key=self.database_key)
        self._table_guid = next(
            table.guid for table in all_tables.tables if table.name == self.table_name
        )

        schema_api = SchemaDatabasesApi(self.admin_client)
        dbs = schema_api.get_all_databases()
        self._database_guid = next(db.guid for db in dbs.databases if db.key == database_key)

        self._history_guid = None
        self._latest_state = None
        self._latest_version_guid = None
        self._latest_version = None

    @property
    def history_guid(self) -> str:
        """Will create record history if it doesn't exist.

        Returns
        -------
        str
        """
        if not self._history_guid:
            self._history_guid = self._get_or_create_history()
        return self._history_guid

    @property
    def table_guid(self) -> str:
        """GUID of the table specified for this class.

        Returns
        -------
        str
        """
        if not self._table_guid:
            raise ValueError
        return self._table_guid

    @property
    def database_guid(self) -> str:
        """GUID of the database specified for this class.

        Returns
        -------
        str
        """
        if not self._database_guid:
            raise ValueError
        return self._database_guid

    @property
    def latest_state(self) -> GsaVersionState:
        if not self._latest_state:
            self._get_latest_version_info()
        return self._latest_state

    @property
    def latest_version(self) -> int:
        if not self._latest_version:
            self._get_latest_version_info()
        return self._latest_version

    @property
    def latest_version_guid(self) -> str:
        if not self._latest_version_guid:
            self._get_latest_version_info()
        return self._latest_version_guid

    def _get_latest_version_info(self) -> None:
        """Update this object with information about the latest version of a specified record history."""

        history_api = RecordsRecordHistoriesApi(self.admin_client)
        history_details = history_api.get_record_history(
            database_key=DB_KEY,
            record_history_guid=self.history_guid,
        )
        self._latest_state = history_details.record_versions[-1].version_state
        self._latest_version = history_details.record_versions[-1].version_number
        self._latest_version_guid = history_details.record_versions[-1].guid

    def _get_or_create_history(self) -> str:
        """Get the GUID for the history with the specified name.

        If the history already exists, just return it. If not, create it and then return it.

        Returns
        -------
        str
            The record history GUID
        """

        # First check if we can find the record
        search_api = SearchApi(self.admin_client)
        search_body = GsaSearchRequest(
            criterion=GsaRecordPropertyCriterion(
                _property=GsaSearchableRecordProperty.RECORDNAME,
                inner_criterion=GsaShortTextDatumCriterion(
                    value=self.history_name,
                ),
            )
        )
        search_results = search_api.database_search(
            database_key=DB_KEY,
            body=search_body,
        )
        # If we got exactly one hit, return it
        record_count = len(search_results.results)
        if record_count == 1:
            return search_results.results[0].record_history_guid
        elif record_count > 1:
            raise RuntimeError(
                f"Too many records found in database with name {self.history_name}. Found "
                f"{record_count}, but expected 0 or 1. Cannot continue."
            )

        history_api = RecordsRecordHistoriesApi(self.admin_client)
        response = history_api.create_record_history(
            database_key=DB_KEY,
            table_guid=self._table_guid,
            body=GsaCreateRecordHistory(name=self.history_name, record_type=GsaRecordType.RECORD),
        )
        return response.guid

    def get_or_create_version(self, required_state: GsaVersionState, required_version: int) -> str:
        """Get the GUID for the record version in the specified state, with the specified version.

        If the version already exists, just return it. If not, attempt to create it first.

        Returns
        -------
        str
            The record history GUID

        Raises
        ------
        VersionControlError
            If the requested state and version could not be created for this history.
        """

        version_guid = self._get_version_guid_in_state(required_state, required_version)
        if version_guid:
            return version_guid

        # We need a released v1 record
        if required_state == GsaVersionState.RELEASED and required_version == 1:
            if self.latest_state == GsaVersionState.UNRELEASED and self.latest_version == 1:
                self._release()
                return self.latest_version_guid

        # We need an unreleased version 2 record
        if required_state == GsaVersionState.UNRELEASED and required_version == 2:
            if self.latest_version == 1 and self.latest_state == GsaVersionState.UNRELEASED:
                # Release v1 and create new unreleased v2
                self._release()
                self._create_new_unreleased()
            elif self.latest_version == 1 and self.latest_state == GsaVersionState.RELEASED:
                # Just create new unreleased v2
                self._create_new_unreleased()
            return self._get_version_guid_in_state(required_state, required_version)

        # We need a superseded version 1 record
        if required_state == GsaVersionState.SUPERSEDED and required_version == 1:
            if self.latest_state == GsaVersionState.UNRELEASED and self.latest_version == 2:
                # If latest version is unreleased v2 is unreleased, release it.
                self._release()
                # Re-fetch the information for the newly-superseded record
            elif self.latest_state == GsaVersionState.UNRELEASED and self.latest_version == 1:
                # If v1 is unreleased, we need to release it, then create a new version,
                # and then release that
                self._release()
                self._create_new_unreleased()
                self._release()
            elif self.latest_state in [
                GsaVersionState.RELEASED,
                GsaVersionState.WITHDRAWN,
            ]:
                # If v1 is released or withdrawn, then create a new version and then release it
                self._create_new_unreleased()
                self._release()
            return self._get_version_guid_in_state(required_state, required_version)

        # If we end up here, either the history was in a state that could not produce the required
        # version, or the specific scenario is not implemented.
        raise VersionControlError(
            history_name=self.history_name,
            required_version_number=required_version,
            required_version_state=required_state,
            current_version_number=self.latest_version,
            current_version_state=self.latest_state,
        )

    def _get_version_guid_in_state(
        self, version_state: GsaVersionState, version_number: int
    ) -> Optional[str]:
        """Get information about a specific version of a record history.

        Parameters
        ----------
        version_state : RecordVersionState
            The state of the required version
        version_number : int
            The version number of the required version

        Returns
        -------
        str | None
            The record version guid, or None if one could not be found

        """
        history_api = RecordsRecordHistoriesApi(self.admin_client)
        history_details = history_api.get_record_history(
            database_key=DB_KEY,
            record_history_guid=self.history_guid,
        )
        for version in history_details.record_versions:
            if version.version_state == version_state and version_number == version.version_number:
                return version.guid

    def _release(self) -> None:
        """Release the latest version guid.

        Raises
        ------
        RuntimeError
            If an error occurs when releasing the record.
        """
        versions_api = RecordsRecordVersionsApi(self.admin_client)
        result = versions_api.release_record_version(
            database_key=DB_KEY,
            table_guid=self._table_guid,
            record_history_guid=self.history_guid,
            record_version_guid=self.latest_version_guid,
        )
        try:
            raise RuntimeError(result.errors)
        except AttributeError:
            pass

    def _create_new_unreleased(self) -> None:
        """Create a new unreleased version of an existing history and update this class
        with the new latest version information.

        Raises
        ------
        RuntimeError
            If an error occurs when creating a new unreleased version.
        """
        versions_api = RecordsRecordVersionsApi(self.admin_client)
        result = versions_api.get_modifiable_record_version(
            database_key=DB_KEY,
            table_guid=self._table_guid,
            record_history_guid=self.history_guid,
            record_version_guid=self.latest_version_guid,
        )
        try:
            raise RuntimeError(result.errors)
        except AttributeError:
            pass
        self._get_latest_version_info()
