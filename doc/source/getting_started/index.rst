Getting started
---------------
To use the ``ansys.grantami.recordlists`` package, you must have access to a
Granta MI server that includes Granta MI Server API.

The ``ansys.grantami.recordlists`` package currently supports Python 3.7
through 3.10 on Windows and Linux.

Installation
~~~~~~~~~~~~
To install the latest release from `PyPI <https://pypi.org/project/ansys-grantami-recordlists/>`_, use
this code:

.. code::

    pip install ansys-grantami-recordlists


Alternatively, to install the latest from ``ansys-grantami-recordlists`` `GitHub <https://github.com/pyansys/grantami-recordlists>`_,
use this code:

.. code::

    pip install git:https://github.com/pyansys/grantami-recordlists.git


To install a local *development* version with Git and Poetry, use this code:

.. code::

    git clone https://github.com/pyansys/grantami-recordlists
    cd grantami-recordlists
    poetry install


The preceding code installs the package and allows you to modify it locally,
with your changes reflected in your Python setup after restarting the Python kernel.

Ansys software requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

Verify your installation
~~~~~~~~~~~~~~~~~~~~~~~~
Check that you can start the RecordLists Client from Python by running this code:

.. code:: python

    >>> from ansys.grantami.recordlists import Connection
    >>> connection = Connection("my.server.name").with_autologon().connect()
    >>> print(connection)

    <ApiClient url: my.server.name>

If you see a response from the server, congratulations. You can start using
the RecordLists client. For information about available queries,
see :ref:`Examples`. For more in-depth descriptions,
consult :ref:`API Reference`.