from ansys.grantami.serverapi_openapi import models


class _ArgNotProvided:
    pass


def extract_identifier(response: models.GrantaServerApiListsDtoRecordListResource):
    """Extract the resource identifier from the provided model."""
    return response.resource_uri.split("/")[-1]
