.. _ref_contributing:

Contributing
############

General guidelines
==================
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to the ``grantami-recordlists``
repository.

The following contribution information is specific to the ``grantami-recordlists``
repository, which is for the Granta MI RecordLists library. This PyAnsys library name
is often used in place of the repository name to provide clarity and improve
readability.

Post issues
------------
Use the `Issues <https://github.com/pyansys/grantami-recordlists/issues>`_ page for
this repository to submit questions, report bugs, and request new features.

To reach the PyAnsys support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.


Developer environment setup
===========================

The project uses ``poetry`` for packaging and dependency management. See the `poetry`_ documentation for installation
instructions.

Clone the source repository
---------------------------

Run the following code to clone and install the latest version of the ``grantami-recordlists``
repository. It installs the package in editable mode, which ensures changes to the code
are immediately visible in the environment. It also installs the required development
dependencies to run the tests, build the docs and build the package.

.. code:: bash

    git clone https://github.com/pyansys/grantami-recordlists
    cd grantami-recordlists
    poetry install --with build,doc,tests

Additional tools
-----------------

Pre-commit
~~~~~~~~~~

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool via:

.. code:: bash

    python -m pip install pre-commit && pre-commit install

Tox
~~~
Tests can be run using `tox`_. The project defines tox test environment in ``tox.ini``.
The following environments commands are provided:

.. vale off

- **tox -e style**: checks for coding style quality.
- **tox -e py**: checks for unit tests.
- **tox -e py-coverage**: checks for unit testing and code coverage.
- **tox -e doc**: checks for documentation building process.

.. vale on

Server access
--------------
Running integration tests and building the examples requires access to a valid Granta MI instance
(see :ref:`ref_software_requirements`.).

External contributors may not have an instance of Granta MI at their disposal. Prior to creating a pull request with the
desired changes, they should make sure that unit tests pass (:ref:`Testing <ref_testing>`), static code validation and
styling pass (:ref:`pre-commit <ref_precommit>`), and that the documentation can be generated successfully without the
examples (:ref:`Documenting <ref_documenting>`).

Continuous Integration on GitHub is configured to run the integration tests and generate the full documentation on
creation and updates of pull requests. Continuous Integration is not configured to run for pull requests from forks.
External contributions require approval from a maintainer for checks to run.

.. _ref_precommit:

Code formatting and styling
===========================

This project adheres with PyAnsys recommendation of styling and formatting. The easiest way to validate changes are
compliant is to run the following command:

.. code:: bash

    pre-commit run --all-files


.. _ref_testing:

Testing
=======

.. _ref_documenting:

Documenting
===========

As per PyAnsys guidelines, the documentation is generated using `Sphinx`_.

For building documentation, you can either run the usual rules provided in the
`Sphinx`_ Makefile, such as:

.. code:: bash

    make -C doc/ html && your_browser_name doc/build/html/index.html

It is strongly recommended to run sphinx with the following extra arguments. They ensure all references are valid, and
turn warnings into errors. CI uses the same configuration, so it is advised to resolve any warnings/errors locally
before pushing changes.

.. code:: bash

    doc> sphinx-build -b html source build -W -n --keep-going

Example notebooks
-----------------
Examples are included in the documentation to give you more context around
the core capabilities described in :ref:`ref_grantami_recordlists_api_reference`.
Additional examples are welcomed, especially if they cover a key use case of the
package that has not yet been covered.

The example scripts are placed in the ``examples`` directory and are included
in the documentation build if the environment variable ``BUILD_EXAMPLES`` is set
to ``True``. Otherwise, a different set of examples is run, to validate the process.

Examples are checked in as scripts using the ``light`` format, see `jupytext`_
for more information. As part of the doc build process, the Python
files are converted back into Jupyter notebooks and are executed, which populates
the output cells.

This conversion between Jupyter notebooks and Python files is performed by
`nb-convert`_. For installation
instructions, see the nb-convert documentation.


.. _poetry: https://python-poetry.org/
.. _pre-commit: https://pre-commit.com/
.. _tox: https://tox.wiki/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _jupytext: https://jupytext.readthedocs.io/en/latest/formats.html
.. _nb-convert: https://nbconvert.readthedocs.io/en/latest/