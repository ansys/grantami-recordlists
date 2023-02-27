from typing import List

from ansys.grantami.serverapi_openapi import models  # type: ignore


class _ArgNotProvided:
    pass


def extract_identifier(response: models.GrantaServerApiListsDtoRecordListResource) -> str:
    """Extract the resource identifier from the provided model."""
    words: List[str] = response.resource_uri.split("/")
    return words[-1]
