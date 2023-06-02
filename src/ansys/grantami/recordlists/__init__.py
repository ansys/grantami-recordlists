"""Pythonic client for GRANTA MI ServerAPI RecordLists."""
import importlib.metadata as importlib_metadata

from ._connection import Connection, RecordListsApiClient
from ._models import (
    BooleanCriterion,
    RecordList,
    RecordListItem,
    SearchCriterion,
    SearchResult,
    UserOrGroup,
    UserRole,
)

__all__ = [
    "Connection",
    "RecordListsApiClient",
    "BooleanCriterion",
    "RecordList",
    "RecordListItem",
    "SearchCriterion",
    "SearchResult",
    "UserOrGroup",
    "UserRole",
]
__version__ = importlib_metadata.version(__name__.replace(".", "-"))
