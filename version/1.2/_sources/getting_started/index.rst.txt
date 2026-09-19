.. _ref_getting_started:

Getting started
###############

.. _ref_software_requirements:

Ansys software requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
Check that you can start the RecordLists client from Python by running this code:

.. code:: python

    >>> from ansys.grantami.recordlists import Connection
    >>> client = Connection("http://my.server.name/mi_servicelayer").with_autologon().connect()
    >>> print(client)

    <RecordListsApiClient url: http://my.server.name/mi_servicelayer>

If you see a response from the server, you have successfully installed the RecordLists package and
you can start using the RecordLists client. See :ref:`ref_grantami_recordlists_examples` for more
examples and :ref:`ref_grantami_recordlists_api_reference` for a full description of the API.
