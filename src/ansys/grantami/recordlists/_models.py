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

"""Models."""
from datetime import datetime
from enum import Enum
from typing import Callable, Iterator, List, Optional, Set, Type, TypeVar, Union

from ansys.grantami.serverapi_openapi.v2025r1 import models as models2025r1
from ansys.grantami.serverapi_openapi.v2025r2 import models
from ansys.openapi.common import Unset

from ._logger import logger


class RecordList:
    """
    Describes a RecordList as obtained from the API.

    Read-only - do not directly instantiate or modify instances of this class.
    """

    def __init__(
        self,
        identifier: str,
        name: str,
        created_timestamp: datetime,
        created_user: "UserOrGroup",
        published: bool,
        is_revision: bool,
        awaiting_approval: bool,
        internal_use: bool,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        last_modified_timestamp: Optional[datetime] = None,
        last_modified_user: Optional["UserOrGroup"] = None,
        published_timestamp: Optional[datetime] = None,
        published_user: Optional["UserOrGroup"] = None,
        parent_record_list_identifier: Optional[str] = None,
    ):
        self._identifier: str = identifier
        self._name: str = name
        self._created_timestamp: datetime = created_timestamp
        self._created_user: UserOrGroup = created_user
        self._published: bool = published
        self._is_revision: bool = is_revision
        self._awaiting_approval: bool = awaiting_approval
        self._internal_use: bool = internal_use

        self._description: Optional[str] = description
        self._notes: Optional[str] = notes
        self._last_modified_timestamp: Optional[datetime] = last_modified_timestamp
        self._last_modified_user: Optional[UserOrGroup] = last_modified_user
        self._published_timestamp: Optional[datetime] = published_timestamp
        self._published_user: Optional[UserOrGroup] = published_user

        self._parent_record_list_identifier: Optional[str] = parent_record_list_identifier

    @property
    def name(self) -> str:
        """
        Name of the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists.RecordListsApiClient.update_list`.
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """
        Description of the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists.RecordListsApiClient.update_list`.
        """
        return self._description

    @property
    def notes(self) -> Optional[str]:
        """
        Notes about the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists.RecordListsApiClient.update_list`.
        """
        return self._notes

    @property
    def identifier(self) -> str:
        """Identifier of the Record List. Read-only."""
        return self._identifier

    @property
    def created_timestamp(self) -> datetime:
        """Datetime at which the Record List was created. Read-only."""
        return self._created_timestamp

    @property
    def created_user(self) -> "UserOrGroup":
        """User who created the Record List. Read-only."""
        return self._created_user

    @property
    def last_modified_timestamp(self) -> Optional[datetime]:
        """Datetime at which the Record List was last modified. Read-only."""
        return self._last_modified_timestamp

    @property
    def last_modified_user(self) -> Optional["UserOrGroup"]:
        """User who last modified the Record List. Read-only."""
        return self._last_modified_user

    @property
    def published_timestamp(self) -> Optional[datetime]:
        """Datetime at which the Record List was published. Read-only."""
        return self._published_timestamp

    @property
    def published_user(self) -> Optional["UserOrGroup"]:
        """User who published/withdrew the Record List. Read-only."""
        return self._published_user

    @property
    def published(self) -> bool:
        """Whether the Record List has been published or not. Read-only."""
        return self._published

    @property
    def is_revision(self) -> bool:
        """Whether the Record List is a revision. Read-only."""
        return self._is_revision

    @property
    def awaiting_approval(self) -> bool:
        """Whether the Record List is awaiting approval to be published or withdrawn. Read-only."""
        return self._awaiting_approval

    @property
    def internal_use(self) -> bool:
        """
        Whether the Record List is for internal use only. Read-only.

        Lists flagged as for internal use are periodically deleted from the system.
        """
        return self._internal_use

    @property
    def parent_record_list_identifier(self) -> Optional[str]:
        """
        Identifier of the parent record list. Read-only.

        Is populated if the record list is a revision of another record list.
        """
        return self._parent_record_list_identifier

    @classmethod
    def _from_model(
        cls,
        model: models.GsaRecordListHeader,
    ) -> "RecordList":
        """Instantiate from a model defined in the auto-generated client code."""
        logger.debug("Deserializing RecordList from API response")
        logger.debug(model.to_str())
        instance = cls(
            name=model.name,
            identifier=model.identifier,
            description=model.description if model.description else None,
            notes=model.notes if model.notes else None,
            created_timestamp=model.created_timestamp,
            created_user=UserOrGroup._from_model(model.created_user),
            is_revision=model.is_revision,
            published=model.published,
            awaiting_approval=model.awaiting_approval,
            internal_use=model.internal_use,
            last_modified_timestamp=model.last_modified_timestamp,
            last_modified_user=UserOrGroup._from_model(model.last_modified_user),
            published_timestamp=model.published_timestamp if model.published_timestamp else None,
            published_user=(
                UserOrGroup._from_model(model.published_user) if model.published_user else None
            ),
            parent_record_list_identifier=(
                model.parent_record_list_identifier if model.parent_record_list_identifier else None
            ),
        )
        return instance

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} name: {self._name}>"


class RecordListItem:
    """
    Describes a :class:`RecordList` item, generally a reference to a record in a Granta MI database.

    If this item was returned by the :meth:`.RecordListsApiClient.get_resolvable_list_items` method,
    then it guaranteed to be resolvable by the current user at the time it was generated. If this
    item was returned by the :meth:`.RecordListsApiClient.get_list_items` then it is not guaranteed
    to be resolvable and care should be taken to ensure that the reference to the record is valid
    before using it.

    Parameters
    ----------
    database_guid : str
       GUID of the database.
    table_guid : str or None
       GUID of the table. Must be provided if this object is added to a RecordList. Optional otherwise.
    record_history_guid : str
       Record History GUID.
    record_version : int, optional
       Record version number - for records in version-controlled tables. If provided, the requested
       version of the record is added to the list. If not provided, the list tracks the latest
       available version of the record.
    """

    def __init__(
        self,
        database_guid: str,
        table_guid: str | None,
        record_history_guid: str,
        record_version: Optional[int] = None,
    ):
        self._database_guid: str = database_guid
        self._table_guid: str | None = table_guid
        self._record_history_guid: str = record_history_guid
        self._record_version: Optional[int] = record_version
        self._record_guid: Optional[str] = None

    @property
    def database_guid(self) -> str:
        """Database GUID."""
        return self._database_guid

    @property
    def table_guid(self) -> str | None:
        """Table GUID."""
        return self._table_guid

    @property
    def record_history_guid(self) -> str:
        """Record History GUID."""
        return self._record_history_guid

    @property
    def record_version(self) -> Optional[int]:
        """Record version number."""
        return self._record_version

    @property
    def record_guid(self) -> Optional[str]:
        """
        Record GUID.

        Only populated if the :class:`RecordListItem` has both been obtained via an API request and
        represents a specific version of a record. See the note on the ``record_version`` parameter
        for this class for more details.
        """
        return self._record_guid

    def __eq__(self, other: object) -> bool:
        """Evaluate equality by checking equality of GUIDs and record version."""
        if not isinstance(other, RecordListItem):
            return False
        return (
            self.database_guid == other.database_guid
            and self.table_guid == other.table_guid
            and self.record_history_guid == other.record_history_guid
            and self.record_version == other.record_version
        )

    @classmethod
    def _from_model(cls, model: models.GsaListItem) -> "RecordListItem":
        """Instantiate from a model defined in the auto-generated client code."""
        logger.debug("Deserializing RecordListItem from API response")
        logger.debug(model.to_str())
        instance = cls(
            database_guid=model.database_guid,
            table_guid=model.table_guid,
            record_history_guid=model.record_history_guid,
            record_version=model.record_version if model.record_version else None,
        )
        instance._record_guid = model.record_guid if model.record_guid else None

        return instance

    def _to_create_list_item_model(self) -> models.GsaCreateListItem:
        """Generate the Create List Item DTO for use with the auto-generated client code."""
        logger.debug("Serializing RecordListItem to GsaCreateListItem API model")
        if self.table_guid is None:
            raise ValueError(
                "table_guid must be provided for a RecordListItem which is added to a RecordList."
            )
        model = models.GsaCreateListItem(
            database_guid=self.database_guid,
            table_guid=self.table_guid,
            record_history_guid=self.record_history_guid,
            record_version=self.record_version,
        )
        logger.debug(model.to_str())
        return model

    def _to_delete_list_item_model(self) -> models.GsaDeleteRecordListItem:
        """Generate the Delete List Item DTO for use with the auto-generated client code."""
        logger.debug("Serializing RecordListItem to GsaDeleteRecordListItem API model")
        model = models.GsaDeleteRecordListItem(
            database_guid=self.database_guid,
            record_history_guid=self.record_history_guid,
            record_version=self.record_version,
        )
        logger.debug(model.to_str())
        return model

    def _to_contains_search_item_model(self) -> models.GsaListItemRecordReference:
        logger.debug("Serializing RecordListItem to GsaListItemRecordReference API model")
        model = models.GsaListItemRecordReference(
            database_guid=self.database_guid,
            record_history_guid=self.record_history_guid,
            record_version=self.record_version,
        )
        logger.debug(model.to_str())
        return model

    def __repr__(self) -> str:
        """Printable representation of the object."""
        properties = {
            "database_guid": f"'{self.database_guid}'",
            "record_history_guid": f"'{self.record_history_guid}'",
        }
        if self.record_version is not None:
            properties["record_version"] = str(self.record_version)
        formatted_properties = ", ".join(f"{name}={value}" for name, value in properties.items())
        return f"<{self.__class__.__name__}({formatted_properties})>"


class UserOrGroup:
    """Description of a Granta MI User or Group.

    Read-only - do not directly instantiate or modify instances of this class.
    """

    def __init__(self) -> None:
        self._identifier: Optional[str] = None
        self._display_name: Optional[str] = None
        self._name: Optional[str] = None

    @property
    def identifier(self) -> Optional[str]:
        """Read-only identifier of the user or group."""
        return self._identifier

    @property
    def display_name(self) -> Optional[str]:
        """Read-only display name of the user or group."""
        return self._display_name

    @property
    def name(self) -> Optional[str]:
        """Read-only name of the user or group."""
        return self._name

    @classmethod
    def _from_model(cls, dto_user: models.GsaListsUserOrGroup) -> "UserOrGroup":
        """Instantiate from a model defined in the auto-generated client code."""
        logger.debug("Deserializing UserOrGroup from API response")
        logger.debug(dto_user.to_str())
        user: UserOrGroup = UserOrGroup()
        user._identifier = dto_user.identifier
        user._display_name = dto_user.display_name
        user._name = dto_user.name
        return user

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} display_name: {self.display_name}>"

    def __eq__(self, other: object) -> bool:
        """Evaluate equality by checking equality of identifiers."""
        if not isinstance(other, UserOrGroup):
            return False
        return self.identifier == other.identifier


class SearchCriterion:
    """
    Search criterion to use in a :meth:`~.RecordListsApiClient.search_for_lists` operation.

    The properties in this class represent an *AND* search - only lists that match all the
    non-null properties will be returned.

    Examples
    --------
    To filter record lists based on their name and status:

    >>> criterion = SearchCriterion(
    ...     name_contains="Approved materials",
    ...     is_published=True,
    ... )

    To filter record lists based on whether they include items from specific databases:

    >>> criterion = SearchCriterion(
    ...     contains_records_in_databases=["9f6182ee-1f49-4ba9-9bd7-d4c0a392e94e"],
    ... )

    To filter record lists based on whether they include items from specific tables:

    >>> criterion = SearchCriterion(
    ...     contains_records_in_tables=["9f6182ee-1f49-4ba9-9bd7-d4c0a392e94e"],
    ... )
    """

    def __init__(
        self,
        name_contains: Optional[str] = None,
        user_role: Optional["UserRole"] = None,
        is_published: Optional[bool] = None,
        is_awaiting_approval: Optional[bool] = None,
        is_internal_use: Optional[bool] = None,
        is_revision: Optional[bool] = None,
        contains_records_in_databases: Optional[List[str]] = None,
        contains_records_in_integration_schemas: Optional[List[str]] = None,
        contains_records_in_tables: Optional[List[str]] = None,
        contains_records: Optional[List["RecordListItem"]] = None,
        user_can_add_or_remove_items: Optional[bool] = None,
    ):
        self._name_contains: Optional[str] = name_contains
        self._user_role: Optional[UserRole] = user_role
        self._is_published: Optional[bool] = is_published
        self._is_awaiting_approval: Optional[bool] = is_awaiting_approval
        self._is_internal_use: Optional[bool] = is_internal_use
        self._is_revision: Optional[bool] = is_revision
        self._contains_records_in_databases: Optional[List[str]] = contains_records_in_databases
        self._contains_records_in_integration_schemas: Optional[List[str]] = (
            contains_records_in_integration_schemas
        )
        self._contains_records_in_tables: Optional[List[str]] = contains_records_in_tables
        self._contains_records: Optional[List["RecordListItem"]] = contains_records
        self._user_can_add_or_remove_items: Optional[bool] = user_can_add_or_remove_items

    @property
    def name_contains(self) -> Optional[str]:
        """Limits results to lists whose name contains the provided string."""
        return self._name_contains

    @name_contains.setter
    def name_contains(self, value: Optional[str]) -> None:
        self._name_contains = value

    @property
    def user_role(self) -> Optional["UserRole"]:
        """Limits results to lists on which the user has the specified role."""
        return self._user_role

    @user_role.setter
    def user_role(self, value: Optional["UserRole"]) -> None:
        self._user_role = value

    @property
    def is_published(self) -> Optional[bool]:
        """
        Limits results to lists with a specific publication status.

        Set to ``True`` to include only record lists that are published.
        Set to ``False`` to include only record lists that are not published.
        Default value ``None`` will include both.
        """
        return self._is_published

    @is_published.setter
    def is_published(self, value: Optional[bool]) -> None:
        self._is_published = value

    @property
    def is_awaiting_approval(self) -> Optional[bool]:
        """
        Limits results to lists with a specific approval status.

        Set to ``True`` to include only record lists that are awaiting approval.
        Set to ``False`` to include only record lists that are not awaiting approval.
        Default value ``None`` will include both.
        """
        return self._is_awaiting_approval

    @is_awaiting_approval.setter
    def is_awaiting_approval(self, value: Optional[bool]) -> None:
        self._is_awaiting_approval = value

    @property
    def is_internal_use(self) -> Optional[bool]:
        """
        Limits results to lists which are internal.

        Set to ``True`` to include only internal record lists.
        Set to ``False`` to include only non-internal record lists.
        Default value ``None`` will include both.
        """
        return self._is_internal_use

    @is_internal_use.setter
    def is_internal_use(self, value: Optional[bool]) -> None:
        self._is_internal_use = value

    @property
    def is_revision(self) -> Optional[bool]:
        """
        Limits results to lists which are revisions.

        Set to ``True`` to include only record lists that are revisions of another list.
        Set to ``False`` to include only record lists that are not revisions.
        Default value ``None`` will include both.
        """
        return self._is_revision

    @is_revision.setter
    def is_revision(self, value: Optional[bool]) -> None:
        self._is_revision = value

    @property
    def contains_records_in_databases(self) -> Optional[List[str]]:
        """Limits results to lists containing records in databases specified by GUIDs."""
        return self._contains_records_in_databases

    @contains_records_in_databases.setter
    def contains_records_in_databases(self, value: Optional[List[str]]) -> None:
        self._contains_records_in_databases = value

    @property
    def contains_records_in_integration_schemas(self) -> Optional[List[str]]:
        """Limits results to lists containing records in integration schemas specified by GUIDs."""
        return self._contains_records_in_integration_schemas

    @contains_records_in_integration_schemas.setter
    def contains_records_in_integration_schemas(self, value: Optional[List[str]]) -> None:
        self._contains_records_in_integration_schemas = value

    @property
    def contains_records_in_tables(self) -> Optional[List[str]]:
        """Limits results to lists containing records in tables specified by GUIDs."""
        return self._contains_records_in_tables

    @contains_records_in_tables.setter
    def contains_records_in_tables(self, value: Optional[List[str]]) -> None:
        self._contains_records_in_tables = value

    @property
    def contains_records(self) -> Optional[List["RecordListItem"]]:
        """Limits results to lists containing specific records.

        When interacting with Granta MI 2025 R1 and earlier, all :class:`.RecordListItem` objects provided to this
        property must contain the same database GUID. To search for lists that contain records in multiple databases,
        use a :class:`.BooleanCriterion` to combine multiple ``SearchCriterion`` objects.

        .. versionchanged:: 2.0
           Changed argument type
        """
        return self._contains_records

    @contains_records.setter
    def contains_records(self, value: Optional[List["RecordListItem"]]) -> None:
        self._contains_records = value

    @property
    def user_can_add_or_remove_items(self) -> Optional[bool]:
        """Limits results to lists where the current user can add or remove items."""
        return self._user_can_add_or_remove_items

    @user_can_add_or_remove_items.setter
    def user_can_add_or_remove_items(self, value: Optional[bool]) -> None:
        self._user_can_add_or_remove_items = value

    def _to_model(self) -> models.GsaRecordListSearchCriterion:
        """
        Generate the DTO for use with the auto-generated client code.

        Generated DTO compatible with Granta MI 2025 R2 and later.
        """
        logger.debug("Serializing SearchCriterion to API model")

        user_role = (
            models.GsaUserRole(self.user_role.value) if self.user_role is not None else Unset
        )

        record_references: List[models.GsaListItemRecordReference] | None
        if self.contains_records is not None:
            record_references = [
                RecordListItem._to_contains_search_item_model(item)
                for item in self.contains_records
            ]
        else:
            record_references = None

        model = models.GsaRecordListSearchCriterion(
            name_contains=self.name_contains,
            user_role=user_role,
            is_published=self.is_published,
            is_awaiting_approval=self.is_awaiting_approval,
            is_internal_use=self.is_internal_use,
            is_revision=self.is_revision,
            contains_records_in_databases=self.contains_records_in_databases,
            contains_records_in_integration_schemas=self.contains_records_in_integration_schemas,
            contains_records_in_tables=self.contains_records_in_tables,
            contains_records=record_references,
            user_can_add_or_remove_items=self.user_can_add_or_remove_items,
        )
        logger.debug(model.to_str())
        return model

    def _to_2025r1_model(self) -> models2025r1.GsaRecordListSearchCriterion:
        """
        Generate the DTO for use with the auto-generated client code.

        Generated DTO compatible with Granta MI 2025 R1 and earlier.
        """
        logger.debug("Serializing SearchCriterion to API model")

        user_role = (
            models2025r1.GsaUserRole(self.user_role.value) if self.user_role is not None else Unset
        )

        record_history_guids: List[str] | None
        database_guids: List[str] | None
        if self.contains_records_in_databases and self.contains_records:
            raise ValueError(
                "When interacting with Granta MI 2025 R1 and earlier, both 'contains_records_in_database' and "
                "'contains_records' cannot be specified for the same criterion."
            )
        elif self.contains_records:
            record_history_guids = [r.record_history_guid for r in self.contains_records]
            _unique_database_guids = {r.database_guid for r in self.contains_records}
            if len(_unique_database_guids) != 1:
                raise ValueError(
                    "When interacting with Granta MI 2025 R1 and earlier, all RecordListItem objects provided to the "
                    "'contains_records' property must contain the same database GUID. To search for lists that contain "
                    "records in multiple databases, use a BooleanCriterion to combine multiple SearchCriterion objects."
                )
            database_guids = list(_unique_database_guids)
        elif self.contains_records_in_databases:
            record_history_guids = None
            database_guids = self.contains_records_in_databases
        else:
            record_history_guids = None
            database_guids = None

        model = models2025r1.GsaRecordListSearchCriterion(
            name_contains=self.name_contains,
            user_role=user_role,
            is_published=self.is_published,
            is_awaiting_approval=self.is_awaiting_approval,
            is_internal_use=self.is_internal_use,
            is_revision=self.is_revision,
            contains_records_in_databases=database_guids,
            contains_records_in_integration_schemas=self.contains_records_in_integration_schemas,
            contains_records_in_tables=self.contains_records_in_tables,
            contains_records=record_history_guids,
            user_can_add_or_remove_items=self.user_can_add_or_remove_items,
        )
        logger.debug(model.to_str())
        return model

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} ...>"


class BooleanCriterion:
    """
    Search criterion to use in a search operation :meth:`~.RecordListsApiClient.search_for_lists`.

    Use this class to combine multiple :class:`SearchCriterion` or
    :class:`BooleanCriterion` objects together as either *AND* or *OR* searches. When both :attr:`.match_any`
    and :attr:`.match_all` are used together, results match all criterion from ``match_all`` *AND* at least one
    criterion from ``match_any``.

    Examples
    --------
    Search record lists and obtain the union of multiple criteria (*OR*):

    >>> criterion = BooleanCriterion(
    ...     match_any=[
    ...         SearchCriterion(name_contains="Approved materials"),
    ...         SearchCriterion(is_published=True),
    ...     ]
    ... )

    Search record lists and obtain the intersection of multiple criteria (*AND*):

    >>> criterion = BooleanCriterion(
    ...     match_all=[
    ...         SearchCriterion(name_contains="Approved materials"),
    ...         SearchCriterion(is_published=True),
    ...     ]
    ... )

    """

    def __init__(
        self,
        match_any: Optional[List[Union["BooleanCriterion", "SearchCriterion"]]] = None,
        match_all: Optional[List[Union["BooleanCriterion", "SearchCriterion"]]] = None,
    ):
        self._match_any = match_any
        self._match_all = match_all

    @property
    def match_any(self) -> Optional[List[Union["BooleanCriterion", "SearchCriterion"]]]:
        """
        Limits results to lists which satisfy one or more provided criteria.

        Returns
        -------
        list of :class:`BooleanCriterion` | :class:`SearchCriterion`, or None
        """
        return self._match_any

    @match_any.setter
    def match_any(
        self, value: Optional[List[Union["BooleanCriterion", "SearchCriterion"]]]
    ) -> None:
        self._match_any = value

    @property
    def match_all(self) -> Optional[List[Union["BooleanCriterion", "SearchCriterion"]]]:
        """
        Limits results to lists which satisfy all provided criteria.

        Returns
        -------
        list of :class:`BooleanCriterion` | :class:`SearchCriterion`, or None
        """
        return self._match_all

    @match_all.setter
    def match_all(
        self, value: Optional[List[Union["BooleanCriterion", "SearchCriterion"]]]
    ) -> None:
        self._match_all = value

    def _to_model(self) -> models.GsaListBooleanCriterion:
        """
        Generate the DTO for use with the auto-generated client code.

        Generated DTO compatible with Granta MI 2025 R2 and later.
        """
        logger.debug("Serializing BooleanCriterion to API model")
        model = models.GsaListBooleanCriterion(
            match_any=(
                [criteria._to_model() for criteria in self.match_any]
                if self.match_any is not None
                else None
            ),
            match_all=(
                [criteria._to_model() for criteria in self.match_all]
                if self.match_all is not None
                else None
            ),
        )
        logger.debug(model.to_str())
        return model

    def _to_2025r1_model(self) -> models2025r1.GsaListBooleanCriterion:
        """
        Generate the DTO for use with the auto-generated client code.

        Generated DTO compatible with Granta MI 2025 R1 and earlier.
        """
        logger.debug("Serializing BooleanCriterion to API model")
        model = models2025r1.GsaListBooleanCriterion(
            match_any=(
                [criteria._to_2025r1_model() for criteria in self.match_any]
                if self.match_any is not None
                else None
            ),
            match_all=(
                [criteria._to_2025r1_model() for criteria in self.match_all]
                if self.match_all is not None
                else None
            ),
        )
        logger.debug(model.to_str())
        return model

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} ...>"


class UserRole(str, Enum):
    """Roles a user can have on a record list.

    Can be used in :attr:`SearchCriterion.user_role`.
    """

    NONE = models.GsaUserRole.NONE.value
    """:class:`UserRole` is currently only supported in searches. Searching for lists with user
    role = :attr:`.NONE` as criteria would exclude all lists from the results."""
    OWNER = models.GsaUserRole.OWNER.value
    SUBSCRIBER = models.GsaUserRole.SUBSCRIBER.value
    CURATOR = models.GsaUserRole.CURATOR.value
    ADMINISTRATOR = models.GsaUserRole.ADMINISTRATOR.value
    PUBLISHER = models.GsaUserRole.PUBLISHER.value


class SearchResult:
    """Describes the result of a search.

    Read-only - do not directly instantiate or modify instances of this class.
    """

    def __init__(self, record_list: RecordList, items: Optional[List[RecordListItem]]):
        self._record_list = record_list
        self._items = items

    @property
    def record_list(self) -> RecordList:
        """Details of the record list associated with the search result."""
        return self._record_list

    @property
    def items(self) -> Optional[List[RecordListItem]]:
        """
        Items of the record list associated with the search result.

        Will be ``None`` unless ``include_items`` has been specified in
        :meth:`~.RecordListsApiClient.search_for_lists`
        """
        return self._items

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} name: {self.record_list.name}>"

    @classmethod
    def _from_model(
        cls,
        model: models.GsaRecordListSearchResult,
        includes_items: bool,
    ) -> "SearchResult":
        """
        Instantiate from a model defined in the auto-generated client code.

        Parameters
        ----------
        model:
            DTO object to parse
        includes_items: bool
            Whether the DTO object includes items.
        """
        logger.debug("Deserializing SearchResult from API response")
        logger.debug(f"List items were{' ' if includes_items else ' not '}requested")
        logger.debug(model.to_str())
        # Set items to None if they have not been requested to allow distinction between list
        # without items and list whose items have not been requested. On the DTO object, both are
        # represented by an empty list.
        items = None
        if includes_items:
            items = [RecordListItem._from_model(item) for item in model.items]

        return cls(
            record_list=RecordList._from_model(model.header),
            items=items,
        )


class AuditLogAction(str, Enum):
    """Action logged involving a specific record list.

    Can be used in :attr:`AuditLogSearchCriterion.filter_actions`.
    """

    LISTCREATED = models.GsaListAction.LISTCREATED.value
    LISTDELETED = models.GsaListAction.LISTDELETED.value
    ITEMADDED = models.GsaListAction.ITEMADDED.value
    ITEMREMOVED = models.GsaListAction.ITEMREMOVED.value
    LISTNAMECHANGED = models.GsaListAction.LISTNAMECHANGED.value
    LISTDESCRIPTIONCHANGED = models.GsaListAction.LISTDESCRIPTIONCHANGED.value
    LISTNOTESCHANGED = models.GsaListAction.LISTNOTESCHANGED.value
    LISTSETTOAWAITINGAPPROVALFORPUBLISHING = (
        models.GsaListAction.LISTSETTOAWAITINGAPPROVALFORPUBLISHING.value
    )
    LISTSETTOAWAITINGAPPROVALFORWITHDRAWAL = (
        models.GsaListAction.LISTSETTOAWAITINGAPPROVALFORWITHDRAWAL.value
    )
    LISTAWAITINGAPPROVALFORPUBLISHINGREMOVED = (
        models.GsaListAction.LISTAWAITINGAPPROVALFORPUBLISHINGREMOVED.value
    )
    LISTAWAITINGAPPROVALFORWITHDRAWALREMOVED = (
        models.GsaListAction.LISTAWAITINGAPPROVALFORWITHDRAWALREMOVED.value
    )
    LISTPUBLISHED = models.GsaListAction.LISTPUBLISHED.value
    LISTUNPUBLISHED = models.GsaListAction.LISTUNPUBLISHED.value
    LISTREVISIONCREATED = models.GsaListAction.LISTREVISIONCREATED.value
    LISTREVISIONDISCARDED = models.GsaListAction.LISTREVISIONDISCARDED.value
    USERSUBSCRIBED = models.GsaListAction.USERSUBSCRIBED.value
    USERUNSUBSCRIBED = models.GsaListAction.USERUNSUBSCRIBED.value
    LISTCURATORADDED = models.GsaListAction.LISTCURATORADDED.value
    LISTCURATORREMOVED = models.GsaListAction.LISTCURATORREMOVED.value
    LISTADMINADDED = models.GsaListAction.LISTADMINADDED.value
    LISTADMINREMOVED = models.GsaListAction.LISTADMINREMOVED.value
    LISTPUBLISHERADDED = models.GsaListAction.LISTPUBLISHERADDED.value
    LISTPUBLISHERREMOVED = models.GsaListAction.LISTPUBLISHERREMOVED.value
    LISTMADEINTERNAL = models.GsaListAction.LISTMADEINTERNAL.value
    LISTMADENOTINTERNAL = models.GsaListAction.LISTMADENOTINTERNAL.value


class AuditLogSearchCriterion:
    """
    Search criterion to use in a search operation :meth:`~.RecordListsApiClient.search_for_lists`.

    Examples
    --------
    Search audit log entries for a given record list.

    >>> criterion = AuditLogSearchCriterion(
    ...    filter_record_lists = []
    ... )

    Search audit log entries for all record lists published or made not internal.

    >>> criterion = AuditLogSearchCriterion(
    ...    filter_actions = {AuditLogAction.LISTPUBLISHED, AuditLogAction.LISTMADENOTINTERNAL}
    ... )
    """

    def __init__(
        self,
        filter_record_lists: Optional[List[str]] = None,
        filter_actions: Optional[Set[AuditLogAction]] = None,
    ):
        self._filter_record_lists = filter_record_lists
        self._filter_actions = filter_actions

    @property
    def filter_record_lists(self) -> Optional[List[str]]:
        """Filter audit log entries for only the specified record list identifiers.

        If None then log entries for all record lists will be included.
        """
        return self._filter_record_lists

    @filter_record_lists.setter
    def filter_record_lists(self, filter_record_lists: Optional[List[str]]) -> None:
        self._filter_record_lists = filter_record_lists

    @property
    def filter_actions(self) -> Optional[Set[AuditLogAction]]:
        """Filter audit log entries for only the specified actions.

        If None then log entries for all actions will be included.
        """
        return self._filter_actions

    @filter_actions.setter
    def filter_actions(self, filter_actions: Optional[Set[AuditLogAction]]) -> None:
        self._filter_actions = filter_actions

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} ...>"

    def _to_model(self) -> models.GsaListAuditLogSearchRequest:
        """Generate the DTO for use with the auto-generated client code."""
        logger.debug("Serializing AuditLogSearchCriterion to API model")
        model = models.GsaListAuditLogSearchRequest(
            list_actions_to_include=(
                [models.GsaListAction(item.value) for item in self.filter_actions]
                if self.filter_actions
                else None
            ),
            list_identifiers=self.filter_record_lists,
        )
        logger.debug(model.to_str())
        return model


class AuditLogItem:
    """
    A log entry representing a single action affecting a record list.

    Read-only - do not directly instantiate or modify instances of this class.
    """

    def __init__(
        self,
        list_identifier: str,
        initiating_user: UserOrGroup,
        user_or_group_affected: Optional[UserOrGroup],
        list_item_affected: Optional[RecordListItem],
        action: AuditLogAction,
        timestamp: datetime,
    ) -> None:
        self._list_identifier = list_identifier
        self._initiating_user = initiating_user
        self._user_or_group_affected = user_or_group_affected
        self._list_item_affected = list_item_affected
        self._action = action
        self._timestamp = timestamp

    @property
    def list_identifier(self) -> str:
        """Identifier of the record list affected by the action that triggered this audit log entry."""
        return self._list_identifier

    @property
    def initiating_user(self) -> UserOrGroup:
        """User or Group that initiated the action that triggered this audit log entry."""
        return self._initiating_user

    @property
    def user_or_group_affected(self) -> Optional[UserOrGroup]:
        """User or group affected by the action that triggered this audit log entry, if applicable."""
        return self._user_or_group_affected

    @property
    def list_item_affected(self) -> Optional[RecordListItem]:
        """Record list item affected by the action that triggered this audit log entry, if applicable."""
        return self._list_item_affected

    @property
    def action(self) -> AuditLogAction:
        """Type of action that triggered this audit log entry."""
        return self._action

    @property
    def timestamp(self) -> datetime:
        """Timestamp of the event that triggered this audit log entry."""
        return self._timestamp

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} list_identifier={self.list_identifier}, action=AuditLogAction.{self.action.name}>"

    @classmethod
    def _from_model(
        cls,
        model: models.GsaListAuditLogItem,
    ) -> "AuditLogItem":
        """
        Instantiate from a model defined in the auto-generated client code.

        Parameters
        ----------
        model:
            DTO object to parse
        """
        logger.debug("Deserializing AuditLogItem from API response")
        logger.debug(model.to_str())

        assert (
            model.list_identifier
        ), "GsaListAuditLogItem must have populated list_identifier attribute"
        assert (
            model.initiating_user
        ), "GsaListAuditLogItem must have populated initiating_user attribute"
        assert model.timestamp, "GsaListAuditLogItem must have populated timestamp attribute"
        assert model.action, "GsaListAuditLogItem must have populated action attribute"

        return cls(
            list_identifier=model.list_identifier,
            initiating_user=UserOrGroup._from_model(model.initiating_user),
            user_or_group_affected=(
                None
                if not model.user_or_group_affected
                else UserOrGroup._from_model(model.user_or_group_affected)
            ),
            list_item_affected=(
                None
                if not model.list_item_affected
                else RecordListItem._from_model(model.list_item_affected)
            ),
            action=AuditLogAction(model.action.value),
            timestamp=model.timestamp,
        )


T = TypeVar("T")


class _PagedResult(Iterator[T]):
    """
    Object representing the result of a search.

    The individual results are obtained by iterating over this object. The results will be
    fetched from the API as and when they are needed.

    To fetch all the results, execute ``list(PagedResult)``.
    """

    def __init__(
        self, next_func: Callable[[int, int], List[T]], iterator_type: Type[T], page_size: int
    ) -> None:
        self._next_func = next_func
        self._page_size = page_size
        self._current_page: Iterator[T] = iter([])
        self._page_index = 0
        self._iterator_type = iterator_type

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__}[{self._iterator_type.__name__}] page_size={self._page_size}>"

    def __iter__(self) -> Iterator[T]:
        """Return the iterator associated with this object."""
        return self

    def __next__(self) -> T:
        """
        Return the next result from the iterator associated with this object.

        Raises
        ------
        StopIteration
          If there are no more elements
        """
        try:
            return next(self._current_page)
        except StopIteration:
            next_page = self._next_func(self._page_size, self._page_index * self._page_size)
            self._page_index += 1
            self._current_page = iter(next_page)

        return next(self._current_page)
