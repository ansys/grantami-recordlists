"""Pythonic client for GRANTA MI ServerAPI RecordLists."""
import importlib.metadata as importlib_metadata

from ._connection import Connection
from .models import RecordList

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
