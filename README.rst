|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black| |pre-commit-ci|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?labelColor=black&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-grantami-recordlists?logo=pypi
   :target: https://pypi.org/project/ansys-grantami-recordlists/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-grantami-recordlists.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-grantami-recordlists
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/grantami-recordlists/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/grantami-recordlists
   :alt: Codecov

.. |GH-CI| image:: https://github.com/pyansys/grantami-recordlists/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/grantami-recordlists/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit-ci| image:: https://results.pre-commit.ci/badge/github/ansys/grantami-recordlists/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/grantami-recordlists/main
   :alt: pre-commit.ci status


PyGranta RecordLists
====================

..
   _after-badges


A Python wrapper for the Granta MI Lists API.


Dependencies
------------
.. readme_software_requirements

This version of the ``ansys.grantami.recordlists`` package requires Granta MI 2024 R2 or newer. Use
`the PyGranta documentation <https://grantami.docs.pyansys.com/version/stable/package_versions>`_ to find the
version of this package compatible with older Granta MI versions.

The ``ansys.grantami.recordlists`` package currently supports Python from version 3.10 to version 3.13.

.. readme_software_requirements_end



Installation
--------------
.. readme_installation

To install the latest release from `PyPI <https://pypi.org/project/ansys-grantami-recordlists/>`_, use
this code:

.. code::

    pip install ansys-grantami-recordlists

To install a release compatible with a specific version of Granta MI, use the
`PyGranta <https://grantami.docs.pyansys.com/>`_ meta-package with a requirement specifier:

.. code::

    pip install pygranta==2023.2.0

To see which individual PyGranta package versions are installed with each version of the PyGranta metapackage, consult
the `Package versions <https://grantami.docs.pyansys.com/version/dev/package_versions.html>`_ section of the PyGranta
documentation.

Alternatively, to install the latest development version from ``ansys-grantami-recordlists`` `GitHub <https://github.com/ansys/grantami-recordlists>`_,
use this code:

.. code::

    pip install git+https://github.com/ansys/grantami-recordlists.git


To install a local *development* version with Git and Poetry, use this code:

.. code::

    git clone https://github.com/ansys/grantami-recordlists
    cd grantami-recordlists
    poetry install


The preceding code installs the package and allows you to modify it locally,
with your changes reflected in your Python setup after restarting the Python kernel.

.. readme_installation_end
