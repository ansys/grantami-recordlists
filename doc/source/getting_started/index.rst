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
Check that you can start the RecordLists Client from Python by running this code:

.. code:: python

    >>> from ansys.grantami.recordlists import Connection
    >>> client = Connection("http://my.server.name/mi_servicelayer").with_autologon().connect()
    >>> print(client)

    <RecordListsApiClient url: http://my.server.name/mi_servicelayer>

If you see a response from the server, congratulations. You can start using
the record lists client. For more detailed examples,
see :ref:`ref_grantami_recordlists_examples`. For more in-depth descriptions,
consult :ref:`ref_grantami_recordlists_api_reference`.