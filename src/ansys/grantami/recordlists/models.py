"""
Models
"""
from datetime import datetime
from functools import wraps
from typing import List, Optional, TYPE_CHECKING

from ansys.grantami.serverapi_openapi import models

if TYPE_CHECKING:
    from ansys.grantami.recordlists._connection import RecordListApiClient


def requires_existence(
    fn,
):
    @wraps(fn)
    def wrapped_property_getter(self: "RecordList"):
        if not self.exists_on_server:
            raise RuntimeError("RecordList must first be created.")  # TODO custom exception
        return fn(self)

    return wrapped_property_getter


class RecordList:
    """
    Describes a RecordList as obtained from the API.
    """

    # TODO Skipped, might be for internal use?
    #  - metadata
    #  - parent_record_list_identifier

    def __init__(
        self,
        client: "RecordListApiClient",
        name: str,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        items: Optional[List["RecordListItem"]] = None,
    ):
        self._client = client

        # Read-only
        # Should not be None if list has been retrieved from server
        self._identifier: Optional[str] = None
        self._created_timestamp: Optional[datetime] = None
        self._created_user: Optional[User] = None
        self._published: Optional[bool] = None
        self._is_revision: Optional[bool] = None
        self._awaiting_approval: Optional[bool] = None
        self._internal_use: Optional[bool] = None
        self._last_modified_timestamp: Optional[datetime] = None
        self._last_modified_user: Optional[User] = None
        # Can be None even if list has been retrieved from server
        self._published_timestamp: Optional[datetime] = None
        self._published_user: Optional[datetime] = None

        # Read/Write
        # Mandatory
        self._name: str = name
        # Optional
        self._description: Optional[None] = description
        self._notes: Optional[None] = notes

        # Other properties not directly extracted from auto-generated RecordListHeader model
        self._items: Optional[List["RecordListItem"]] = items

    @property
    def exists_on_server(self) -> bool:
        """Whether the list exists on server or has been created in memory only."""
        return self._identifier is not None

    # Read & Write properties

    @property
    def name(self) -> str:
        """
        Name of the Record List.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Set the name of the Record List
        """
        if self.exists_on_server:
            # TODO support update
            raise ValueError("Cannot set the value of property 'name'. Use [] instead.")
        self._name = value

    @property
    def description(self) -> str:
        """
        Description of the Record List.
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """
        Set the description of the Record List
        """
        if self.exists_on_server:
            # TODO support update
            raise ValueError("Cannot set the value of property 'description'. Use [] instead.")
        self._description = value

    @property
    def notes(self) -> str:
        """
        Notes about the Record List.
        """
        return self._description

    @notes.setter
    def notes(self, value: str):
        """
        Set the notes of the Record List
        """
        if self.exists_on_server:
            # TODO support update
            raise ValueError("Cannot set the value of property 'notes'. Use [] instead.")
        self._notes = value

    # Read-only properties

    @property
    @requires_existence
    def identifier(self) -> str:
        """
        Identifier of the Record List.
        Read-only.
        """
        return self._identifier

    @property
    @requires_existence
    def created_timestamp(self) -> datetime:
        """
        Datetime at which the Record List was created.
        Read-only.
        """
        return self._created_timestamp

    @property
    @requires_existence
    def created_user(self) -> "User":
        """
        User who created the Record List.
        Read-only.
        """
        return self._created_user

    @property
    @requires_existence
    def last_modified_timestamp(self) -> datetime:
        """
        Datetime at which the Record List was last modified.
        Read-only.
        """
        return self._last_modified_timestamp

    @property
    @requires_existence
    def last_modified_user(self) -> "User":
        """
        User who last modified the Record List.
        Read-only.
        """
        return self._last_modified_user

    @property
    @requires_existence
    def published_timestamp(self) -> Optional[datetime]:
        """
        Datetime at which the Record List was published.
        Read-only.
        """
        # TODO also represents last withdrawal date. Consider renaming
        return self._published_timestamp

    @property
    @requires_existence
    def published_user(self) -> Optional["User"]:
        """
        Datetime at which the Record List was published.
        Read-only.
        """
        # TODO also represents last withdrawal date. Consider renaming
        return self._published_user

    @property
    @requires_existence
    def published(self) -> bool:
        """
        Whether the Record List has been published or not.
        Read-only.
        """
        return self._published

    @property
    @requires_existence
    def is_revision(self) -> bool:
        """
        Whether the Record List is a revision.
        Read-only.
        """
        return self._is_revision

    @property
    @requires_existence
    def awaiting_approval(self) -> bool:
        """
        Whether the Record List is awaiting approval to be published or withdrawn.
        Read-only.
        """
        return self._awaiting_approval

    @property
    @requires_existence
    def internal_use(self) -> bool:
        """
        Whether the Record List is for internal use only.
        Read-only.
        """
        # TODO internal_use flags that the list has been created by another MI application. Internal
        #  lists are periodically deleted.
        #  Consider not exposing the property and filtering out all internal lists?
        return self._internal_use

    # Item management

    def read_items(self):
        """
        Fetches items included in the RecordList via a request to ServerAPI
        """
        self._items = self._client.get_list_items(self._identifier)

    @property
    def items(self) -> List["RecordListItem"]:
        """
        Items included in the RecordList. Fetched from ServerAPI if not yet exported.
        """
        if self._items is None:
            self.read_items()
        return self._items

    def add_items(self, items: List["RecordListItem"]):
        """
        Add items to the RecordList and refreshes all items.
        Might be successful even if the items are invalid references.
        """
        if self.exists_on_server:
            self._client.add_items_to_list(self._identifier, items)
            self.read_items()
        else:
            if self._items is None:
                self._items = []
            self._items.extend(items)

    def remove_items(self, items: List["RecordListItem"]):
        """
        Remove items from the RecordList and refetches current items from ServerAPI.
        Might be successful even the items are not initially in the RecordList.
        """
        # TODO: API will accept removal of items that are not in the list.
        #  We could check here that items are in the list and raise an Exception if not, although it
        #  would require getting the items first.
        if self.exists_on_server:
            self._client.remove_items_from_list(self._identifier, items=items)
            self.read_items()
        else:
            if self._items is None:
                self._items = []
            for item in items:
                self._items.remove(item)

    @classmethod
    def from_model(
        cls,
        client: "RecordListApiClient",
        model: models.GrantaServerApiListsDtoRecordListHeader,
        items: models.GrantaServerApiListsDtoRecordListItems = None,
    ):
        """
        Instantiate from a model defined in the auto-generated client code.
        """
        instance = cls(
            client,
            model.name,
            model.description,
            model.notes,
        )
        instance._from_model(model, items)
        return instance

    def _from_model(
        self,
        model: models.GrantaServerApiListsDtoRecordListHeader,
        items: models.GrantaServerApiListsDtoRecordListItems = None,
    ):
        """Set private properties (read-only list properties)"""
        self._identifier = model.identifier
        self._created_timestamp = model.created_timestamp
        self._created_user = User.from_model(model.created_user)
        self._last_modified_timestamp = model.last_modified_timestamp
        self._last_modified_user = User.from_model(model.last_modified_user)
        self._published_timestamp = model.published_timestamp
        self._published_user = User.from_model(model.published_user)
        self._is_revision = model.is_revision
        self._published = model.published
        self._awaiting_approval = model.awaiting_approval
        self._internal_use = model.internal_use

        if items is not None:
            self._items = [RecordListItem.from_model(list_item) for list_item in items.items]

    def create(self):
        """Multiple requests: create, get, get_items"""
        if self.exists_on_server:
            raise RuntimeError(
                "Cannot create a RecordList that already exists on server. See .copy() or .revise()"
                " to create a copy or private copy of the list."
            )
        created_id = self._client._create_list(
            name=self._name,
            description=self._description,
            notes=self._notes,
            items=self._items,
        )
        details = self._client._get_list(created_id)
        self._from_model(details)

        if self._items is not None:
            self.read_items()


class RecordListItem:
    # TODO add record guid and version, validate input (require one guid)

    def __init__(
        self,
        database_guid: str,
        table_guid: str,
        record_history_guid: str,
    ):
        self._database_guid: str = database_guid
        self._table_guid: str = table_guid
        self._record_history_guid: str = record_history_guid
        # self._record_guid = None
        # self._record_version = None

    @property
    def database_guid(self) -> str:
        return self._database_guid

    @database_guid.setter
    def database_guid(self, value: str):
        self._database_guid = value

    @property
    def table_guid(self) -> str:
        return self._table_guid

    @table_guid.setter
    def table_guid(self, value: str):
        self._table_guid = value

    @property
    def record_history_guid(self) -> str:
        return self._record_history_guid

    @record_history_guid.setter
    def record_history_guid(self, value: str):
        self._record_history_guid = value

    @classmethod
    def from_model(cls, model: models.GrantaServerApiListsDtoListItem):
        return cls(
            database_guid=model.database_guid,
            table_guid=model.table_guid,
            record_history_guid=model.record_history_guid,
        )

    def to_model(self) -> models.GrantaServerApiListsDtoListItem:
        """
        Instantiate from a model defined in the auto-generated client code.
        """
        return models.GrantaServerApiListsDtoListItem(
            database_guid=self.database_guid,
            table_guid=self.table_guid,
            record_history_guid=self.record_history_guid,
        )


class User:
    # TODO change name to something user-friendly that means User AND Group
    """Read-only description of a Granta MI User or Group"""

    def __init__(self):
        self._identifier: Optional[str] = None
        self._display_name: Optional[str] = None
        self._name: Optional[str] = None

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def from_model(
        cls, dto_user: Optional[models.GrantaServerApiListsDtoUserOrGroup]
    ) -> Optional["User"]:
        if dto_user is None:
            return None

        user = User()
        user._identifier = dto_user.identifier
        user._display_name = dto_user.display_name
        user._name = dto_user.name
        return user
