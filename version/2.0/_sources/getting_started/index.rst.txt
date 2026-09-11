.. _ref_getting_started:

Getting started
###############

.. _ref_software_requirements:

Software requirements
~~~~~~~~~~~~~~~~~~~~~
.. include:: ../../../README.rst
      :start-after: readme_software_requirements
      :end-before: readme_software_requirements_end


Installation
~~~~~~~~~~~~
.. include:: ../../../README.rst
      :start-after: readme_installation
      :end-before: readme_installation_end


Verify your installation
~~~~~~~~~~~~~~~~~~~~~~~~
Check that you can start the PyGranta RecordLists client from Python by running this code:

.. code:: python

    >>> from ansys.grantami.recordlists import Connection
    >>> client = Connection("http://my.server.name/mi_servicelayer").with_autologon().connect()
    >>> print(client)

    <RecordListsApiClient url: http://my.server.name/mi_servicelayer>

This example uses Windows-based autologon authentication. For all supported authentication schemes, see the :OpenAPI-Common:`OpenAPI-Common documentation <index.html#authentication-schemes>`.

If you see a response from the server, you have successfully installed PyGranta RecordLists and
can start using the RecordLists client. For more examples, see
:ref:`ref_grantami_recordlists_examples`. For comprehensive information on the API, see
:ref:`ref_grantami_recordlists_api_reference`.
