"""Models."""
from datetime import datetime
from typing import Optional

from ansys.grantami.serverapi_openapi import models  # type: ignore


class RecordList:
    # TODO Skipped, might be for internal use?
    #  - metadata
    """Describes a RecordList as obtained from the API. Read-only."""

    def __init__(
        self,
        identifier: str,
        name: str,
        created_timestamp: datetime,
        created_user: "User",
        published: bool,
        is_revision: bool,
        awaiting_approval: bool,
        internal_use: bool,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        # TODO is set at creation, so not optional?
        last_modified_timestamp: Optional[datetime] = None,
        # TODO is set at creation, so not optional?
        last_modified_user: Optional["User"] = None,
        published_timestamp: Optional[datetime] = None,
        published_user: Optional["User"] = None,
        parent_record_list_identifier: Optional[str] = None,
    ):

        self._identifier: str = identifier
        self._name: str = name
        self._created_timestamp: datetime = created_timestamp
        self._created_user: User = created_user
        self._published: bool = published
        self._is_revision: bool = is_revision
        self._awaiting_approval: bool = awaiting_approval
        self._internal_use: bool = internal_use

        self._description: Optional[str] = description
        self._notes: Optional[str] = notes
        self._last_modified_timestamp: Optional[datetime] = last_modified_timestamp
        self._last_modified_user: Optional[User] = last_modified_user
        self._published_timestamp: Optional[datetime] = published_timestamp
        self._published_user: Optional[User] = published_user

        self._parent_record_list_identifier: Optional[str] = parent_record_list_identifier

    @property
    def name(self) -> str:
        """
        Name of the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists._connection.RecordListApiClient.update_list`.
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """
        Description of the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists._connection.RecordListApiClient.update_list`.
        """
        return self._description

    @property
    def notes(self) -> Optional[str]:
        """
        Notes about the Record List. Read-only.

        Can be updated via
        :meth:`~ansys.grantami.recordlists._connection.RecordListApiClient.update_list`.
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
    def created_user(self) -> "User":
        """User who created the Record List. Read-only."""
        return self._created_user

    @property
    def last_modified_timestamp(self) -> Optional[datetime]:
        """Datetime at which the Record List was last modified. Read-only."""
        return self._last_modified_timestamp

    @property
    def last_modified_user(self) -> Optional["User"]:
        """User who last modified the Record List. Read-only."""
        return self._last_modified_user

    @property
    def published_timestamp(self) -> Optional[datetime]:
        """Datetime at which the Record List was published. Read-only."""
        # TODO also represents last withdrawal date. Consider renaming
        return self._published_timestamp

    @property
    def published_user(self) -> Optional["User"]:
        """User who published/withdrew the Record List. Read-only."""
        # TODO also represents last withdrawal date. Consider renaming
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
        # TODO internal_use flags that the list has been created by another MI application. Internal
        #  lists are periodically deleted.
        #  Consider not exposing the property and filtering out all internal lists?
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
            created_user=User._from_model(model.created_user),
            is_revision=model.is_revision,
            published=model.published,
            awaiting_approval=model.awaiting_approval,
            internal_use=model.internal_use,
            last_modified_timestamp=model.last_modified_timestamp,
            last_modified_user=User._from_model(model.last_modified_user),
            published_timestamp=model.published_timestamp,
            published_user=User._from_model(model.published_user) if model.published_user else None,
            parent_record_list_identifier=model.parent_record_list_identifier,
        )
        return instance


class RecordListItem:
    """
    Describes an item of a :class:`RecordList`, i.e. a record in a Granta MI database.

    An item does not necessarily represent a record that exists on the server.
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
        represents a record in a version-controlled table.
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


class User:
    # TODO change name to something user-friendly that means User AND Group
    """Read-only description of a Granta MI User or Group."""

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
    def _from_model(cls, dto_user: models.GrantaServerApiListsDtoUserOrGroup) -> "User":
        """Instantiate from a model defined in the auto-generated client code."""
        user: User = User()
        user._identifier = dto_user.identifier
        user._display_name = dto_user.display_name
        user._name = dto_user.name
        return user
