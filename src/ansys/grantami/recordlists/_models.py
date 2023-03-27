"""Models."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from ansys.grantami.serverapi_openapi import models  # type: ignore


class RecordList:
    """
    Describes a RecordList as obtained from the API.

    Read-only - users are never expected to instantiate this class or modify instances of the
    class.
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
        :meth:`~ansys.grantami.recordlists.RecordListApiClient.update_list`.
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """
        Description of the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists.RecordListApiClient.update_list`.
        """
        return self._description

    @property
    def notes(self) -> Optional[str]:
        """
        Notes about the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists.RecordListApiClient.update_list`.
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
        model: models.GrantaServerApiListsDtoRecordListHeader,
    ) -> "RecordList":
        """Instantiate from a model defined in the auto-generated client code."""
        instance = cls(
            name=model.name,
            identifier=model.identifier,
            description=model.description,
            notes=model.notes,
            created_timestamp=model.created_timestamp,
            created_user=UserOrGroup._from_model(model.created_user),
            is_revision=model.is_revision,
            published=model.published,
            awaiting_approval=model.awaiting_approval,
            internal_use=model.internal_use,
            last_modified_timestamp=model.last_modified_timestamp,
            last_modified_user=UserOrGroup._from_model(model.last_modified_user),
            published_timestamp=model.published_timestamp,
            published_user=UserOrGroup._from_model(model.published_user)
            if model.published_user
            else None,
            parent_record_list_identifier=model.parent_record_list_identifier,
        )
        return instance

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} name: {self._name}>"


class RecordListItem:
    """
    Describes an item of a :class:`RecordList`, i.e. a record in a Granta MI database.

    An item does not necessarily represent a record that exists on the server.

    Parameters
    ----------
    database_guid : str
       GUID of the database.
    table_guid : str
       GUID of the table.
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
        table_guid: str,
        record_history_guid: str,
        record_version: Optional[int] = None,
    ):
        self._database_guid: str = database_guid
        self._table_guid: str = table_guid
        self._record_history_guid: str = record_history_guid
        self._record_version: Optional[int] = record_version
        self._record_guid: Optional[str] = None

    @property
    def database_guid(self) -> str:
        """GUID of the database."""
        return self._database_guid

    @property
    def table_guid(self) -> str:
        """GUID of the table."""
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

        Only populated if the :class:`RecordListItem` has been obtained via an API request and
        represents a specific version of a record, specified with
        :attr:`~RecordListItem.record_version`.
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
    def _from_model(cls, model: models.GrantaServerApiListsDtoListItem) -> "RecordListItem":
        """Instantiate from a model defined in the auto-generated client code."""
        instance = cls(
            database_guid=model.database_guid,
            table_guid=model.table_guid,
            record_history_guid=model.record_history_guid,
            record_version=model.record_version,
        )
        instance._record_guid = model.record_guid
        return instance

    def _to_model(self) -> models.GrantaServerApiListsDtoListItem:
        """Generate the DTO for use with the auto-generated client code."""
        return models.GrantaServerApiListsDtoListItem(
            database_guid=self.database_guid,
            table_guid=self.table_guid,
            record_history_guid=self.record_history_guid,
            record_version=self.record_version,
        )


class UserOrGroup:
    """Description of a Granta MI User or Group.

    Read-only - users are never expected to instantiate this class or modify instances of the
    class.
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
    def _from_model(cls, dto_user: models.GrantaServerApiListsDtoUserOrGroup) -> "UserOrGroup":
        """Instantiate from a model defined in the auto-generated client code."""
        user: UserOrGroup = UserOrGroup()
        user._identifier = dto_user.identifier
        user._display_name = dto_user.display_name
        user._name = dto_user.name
        return user


class SearchCriterion:
    """
    Search criterion to use in a :meth:`~.RecordListApiClient.search_for_lists` operation.

    The properties in this class represent an AND search - only lists that match all the
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
        contains_records: Optional[List[str]] = None,
        user_can_add_or_remove_items: Optional[bool] = None,
    ):
        self._name_contains: Optional[str] = name_contains
        self._user_role: Optional[UserRole] = user_role
        self._is_published: Optional[bool] = is_published
        self._is_awaiting_approval: Optional[bool] = is_awaiting_approval
        self._is_internal_use: Optional[bool] = is_internal_use
        self._is_revision: Optional[bool] = is_revision
        self._contains_records_in_databases: Optional[List[str]] = contains_records_in_databases
        self._contains_records_in_integration_schemas: Optional[
            List[str]
        ] = contains_records_in_integration_schemas
        self._contains_records_in_tables: Optional[List[str]] = contains_records_in_tables
        self._contains_records: Optional[List[str]] = contains_records
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
    def contains_records(self) -> Optional[List[str]]:
        """Limits results to lists containing records specified by their history GUIDs."""
        return self._contains_records

    @contains_records.setter
    def contains_records(self, value: Optional[List[str]]) -> None:
        self._contains_records = value

    @property
    def user_can_add_or_remove_items(self) -> Optional[bool]:
        """Limits results to lists where the current user can add or remove items."""
        return self._user_can_add_or_remove_items

    @user_can_add_or_remove_items.setter
    def user_can_add_or_remove_items(self, value: Optional[bool]) -> None:
        self._user_can_add_or_remove_items = value

    def _to_model(self) -> models.GrantaServerApiListsDtoRecordListSearchCriterion:
        """Generate the DTO for use with the auto-generated client code."""
        return models.GrantaServerApiListsDtoRecordListSearchCriterion(
            name_contains=self.name_contains,
            user_role=self.user_role,
            is_published=self.is_published,
            is_awaiting_approval=self.is_awaiting_approval,
            is_internal_use=self.is_internal_use,
            is_revision=self.is_revision,
            contains_records_in_databases=self.contains_records_in_databases,
            contains_records_in_integration_schemas=self.contains_records_in_integration_schemas,
            contains_records_in_tables=self.contains_records_in_tables,
            contains_records=self.contains_records,
            user_can_add_or_remove_items=self.user_can_add_or_remove_items,
        )


class BooleanCriterion:
    """
    Search criterion to use in a search operation :meth:`~.RecordListApiClient.search_for_lists`.

    Allow aggregation of multiple criteria defined as :class:`SearchCriterion` or
    :class:`BooleanCriterion`.

    Examples
    --------
    Search record lists and obtain the union of multiple criteria:

    >>> criterion = BooleanCriterion(
    ...     match_any=[
    ...         SearchCriterion(name_contains="Approved materials"),
    ...         SearchCriterion(is_published=True),
    ...     ]
    ... )

    Search record lists and obtain the intersection of multiple criteria:

    >>> criterion = BooleanCriterion(
    ...     match_all=[
    ...         SearchCriterion(name_contains="Approved materials"),
    ...         SearchCriterion(is_published=True),
    ...     ]
    ... )

    """

    # TODO Using both match_any and match_all ignores criteria in match_any (PUD-561)

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

    def _to_model(self) -> models.GrantaServerApiListsDtoListBooleanCriterion:
        """Generate the DTO for use with the auto-generated client code."""
        return models.GrantaServerApiListsDtoListBooleanCriterion(
            match_any=[criteria._to_model() for criteria in self.match_any]
            if self.match_any is not None
            else None,
            match_all=[criteria._to_model() for criteria in self.match_all]
            if self.match_all is not None
            else None,
        )


class UserRole(str, Enum):
    """Roles a user can have on a record list.

    Can be used in :attr:`SearchCriterion.user_role`.
    """

    NONE = models.GrantaServerApiListsDtoUserRole.NONE
    """:class:`UserRole` is currently only supported in searches. Searching for lists with user
    role = :attr:`.NONE` as criteria would exclude all lists from the results."""
    OWNER = models.GrantaServerApiListsDtoUserRole.OWNER
    SUBSCRIBER = models.GrantaServerApiListsDtoUserRole.SUBSCRIBER
    CURATOR = models.GrantaServerApiListsDtoUserRole.CURATOR
    ADMINISTRATOR = models.GrantaServerApiListsDtoUserRole.ADMINISTRATOR
    PUBLISHER = models.GrantaServerApiListsDtoUserRole.PUBLISHER


class SearchResult:
    """Describes the result of a search.

    Read-only - users are never expected to instantiate this class or modify instances of the
    class.
    """

    def __init__(self, list_details: RecordList, items: Optional[List[RecordListItem]]):
        self._list_details = list_details
        self._items = items

    @property
    def list_details(self) -> RecordList:
        """Details of the record list associated with the search result."""
        return self._list_details

    @property
    def items(self) -> Optional[List[RecordListItem]]:
        """
        Items of the record list associated with the search result.

        Will be ``None`` unless ``include_items`` has been specified in
        :meth:`~.RecordListApiClient.search_for_lists`
        """
        return self._items

    def __repr__(self) -> str:
        """Printable representation of the object."""
        return f"<{self.__class__.__name__} name: {self.list_details.name}>"

    @classmethod
    def _from_model(
        cls,
        model: models.GrantaServerApiListsDtoRecordListSearchResult,
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
        # Set items to None if they have not been requested to allow distinction between list
        # without items and list whose items have not been requested. On the DTO object, both are
        # represented by an empty list.
        items = None
        if includes_items:
            items = [RecordListItem._from_model(item) for item in model.items]

        return cls(
            list_details=RecordList._from_model(model.header),
            items=items,
        )
