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
repository, which is for the PyGranta RecordLists library. This PyAnsys library name
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

.. _ref_tox:

Tox
~~~
Tests can be run using `tox`_. The project defines the tox environments in ``tox.ini``.
The following tox environments are provided:

.. vale off

- ``tox -e style``: checks for coding style quality.
- ``tox -e py``: runs all tests (see :ref:`ref_serveraccess` for requirements).
- ``tox -e py-coverage``: runs all tests and checks code coverage.
- ``tox -e doc``: checks the documentation building process.

.. vale on

Optionally add the ``-- -m "not integration"`` suffix to the commands above to skip integration
tests. For example, ``tox -e py -- -m "not integration"`` will only run tests that
do not require a Granta MI instance.

.. _ref_serveraccess:

Server access
--------------

Running integration tests and building the examples requires access to a valid Granta MI instance
(see :ref:`ref_software_requirements`).

External contributors may not have an instance of Granta MI at their disposal. Prior to creating a pull request with the
desired changes, they should make sure that unit tests pass (:ref:`ref_tox`), static code validation and
styling pass (:ref:`pre-commit <ref_precommit>`), and that the documentation can be generated successfully without the
examples (:ref:`Documenting <ref_documenting>`).

Continuous Integration (CI) on GitHub is configured to run the integration tests and generate the full documentation on
creation and updates of pull requests. CI is not configured to run for pull requests from forks. External contributions
require approval from a maintainer for checks to run.


.. _ref_precommit:

Code formatting and styling
===========================

This project adheres with PyAnsys recommendation of styling and formatting. The easiest way to validate changes are
compliant is to run the following command:

.. code:: bash

    pre-commit run --all-files


.. _ref_documenting:

Documenting
===========

As per PyAnsys guidelines, the documentation is generated using `Sphinx`_.

For building documentation, use the `Sphinx`_ Makefile:

.. code:: bash

    make -C doc/ html && your_browser_name doc/build/html/index.html

If any changes have been made to the documentation, it is strongly recommended
to run sphinx directly with the following extra arguments. They ensure all references
are valid, and turn warnings into errors. CI uses the same configuration, so it is
advised to resolve any warnings/errors locally before pushing changes.

.. code:: bash

    sphinx-build -b html source build -W -n --keep-going


Example notebooks
-----------------
Examples are included in the documentation to give you more context around
the core capabilities described in :ref:`ref_grantami_recordlists_api_reference`.
Additional examples are welcomed, especially if they cover a key use case of the
package that has not yet been covered.

The example scripts are placed in the ``examples`` directory and are included
in the documentation build if the environment variable ``BUILD_EXAMPLES`` is set
to ``True``. Otherwise, a different set of examples is run to validate the process.

Examples are checked in as scripts using the ``light`` format, see `jupytext`_
for more information. As part of the doc build process, the Python
files are converted back into Jupyter notebooks and the output cells are populated
by running the notebooks against a Granta MI instance.

This conversion between Jupyter notebooks and Python files is performed by
`nb-convert`_. For installation instructions, see the nb-convert documentation.


.. _poetry: https://python-poetry.org/
.. _pre-commit: https://pre-commit.com/
.. _tox: https://tox.wiki/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _jupytext: https://jupytext.readthedocs.io/en/latest/formats.html
.. _nb-convert: https://nbconvert.readthedocs.io/en/latest/
