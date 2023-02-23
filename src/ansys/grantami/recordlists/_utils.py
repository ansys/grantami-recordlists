from ansys.grantami.serverapi_openapi import models


class _ArgNotProvided:
    pass


def extract_identifier(response: models.GrantaServerApiListsDtoRecordListResource):
    return response.resource_uri.split("/")[-1]
