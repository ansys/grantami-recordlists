"""Pythonic client for GRANTA MI ServerAPI RecordLists."""
from ._connection import Connection
from .models import RecordList

import importlib.metadata as importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
