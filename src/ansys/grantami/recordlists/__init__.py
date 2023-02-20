"""Pythonic client for GRANTA MI ServerAPI RecordLists."""
from ._connection import Connection
from .models import RecordList

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
