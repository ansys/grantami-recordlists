.. _ref_grantami_recordlists_connection:

Granta MI connection
====================

The OpenAPI-Common documentation lists supported `Authentication schemes <https://openapi.docs.pyansys.com/version/stable/index.html#authentication-schemes>`_.

Connection builder
~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.recordlists.Connection
    :members:

    .. automethod:: with_autologon
    .. automethod:: with_credentials
    .. automethod:: with_oidc
    .. automethod:: with_anonymous

RecordLists client
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.recordlists.RecordListsApiClient
   :members:

