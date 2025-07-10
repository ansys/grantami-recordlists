.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

See `CHANGELOG.md <https://github.com/ansys/grantami-recordlists/blob/main/CHANGELOG.md>`_ for release notes for v1.3.0 and earlier.

.. vale off

.. towncrier release notes start

`2.0.0 <https://github.com/ansys/grantami-recordlists/releases/tag/v2.0.0>`_ - July 10, 2025
============================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add Support for List Operation Audit Logging
          - `#358 <https://github.com/ansys/grantami-recordlists/pull/358>`_

        * - Change type of contains_record search to take a RecordListItem
          - `#361 <https://github.com/ansys/grantami-recordlists/pull/361>`_

        * - Perform additional mypy type checking
          - `#402 <https://github.com/ansys/grantami-recordlists/pull/402>`_

        * - Re-organize ApiClient hierarchy
          - `#413 <https://github.com/ansys/grantami-recordlists/pull/413>`_

        * - Allow table_guid to be None when searching for and deleting list items
          - `#417 <https://github.com/ansys/grantami-recordlists/pull/417>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Handle missing Granta MI version for integration tests
          - `#378 <https://github.com/ansys/grantami-recordlists/pull/378>`_

        * - Fix 2025R2 integration tests
          - `#398 <https://github.com/ansys/grantami-recordlists/pull/398>`_

        * - Update the VM used to build the documentation
          - `#438 <https://github.com/ansys/grantami-recordlists/pull/438>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump serverapi to 5.0.0dev396
          - `#363 <https://github.com/ansys/grantami-recordlists/pull/363>`_

        * - Add tests against multiple Granta MI versions
          - `#374 <https://github.com/ansys/grantami-recordlists/pull/374>`_

        * - Update ansys-openapi-common to v2.2.2
          - `#379 <https://github.com/ansys/grantami-recordlists/pull/379>`_

        * - Tighten serverapi-openapi version specifier
          - `#420 <https://github.com/ansys/grantami-recordlists/pull/420>`_

        * - Remove private PyPI references
          - `#421 <https://github.com/ansys/grantami-recordlists/pull/421>`_

        * - Prepare 2.0.0rc0 release
          - `#437 <https://github.com/ansys/grantami-recordlists/pull/437>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Prepare 2.0.0 release
          - `#459 <https://github.com/ansys/grantami-recordlists/pull/459>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Clarify audit log search behavior
          - `#401 <https://github.com/ansys/grantami-recordlists/pull/401>`_

        * - Improve documentation for Granta MI version support
          - `#415 <https://github.com/ansys/grantami-recordlists/pull/415>`_

        * - Include changelog in documentation
          - `#427 <https://github.com/ansys/grantami-recordlists/pull/427>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update version number on main to v1.4.0.dev0
          - `#350 <https://github.com/ansys/grantami-recordlists/pull/350>`_

        * - chore: update CHANGELOG for v1.3.0
          - `#352 <https://github.com/ansys/grantami-recordlists/pull/352>`_

        * - Update ansys/pre-commit-hooks to 0.5.1
          - `#362 <https://github.com/ansys/grantami-recordlists/pull/362>`_

        * - Bump version to 2.0.0.dev1
          - `#364 <https://github.com/ansys/grantami-recordlists/pull/364>`_

        * - Shutdown all VMs
          - `#372 <https://github.com/ansys/grantami-recordlists/pull/372>`_

        * - Start Granta MI 2024 R1 test machine
          - `#377 <https://github.com/ansys/grantami-recordlists/pull/377>`_

        * - Fix Dependabot Configuration for Private PyPI
          - `#380 <https://github.com/ansys/grantami-recordlists/pull/380>`_

        * - Bump version to 2.0.0.dev2
          - `#390 <https://github.com/ansys/grantami-recordlists/pull/390>`_

        * - docs: Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#391 <https://github.com/ansys/grantami-recordlists/pull/391>`_

        * - Use PyPI-authored publish action
          - `#405 <https://github.com/ansys/grantami-recordlists/pull/405>`_

        * - Generate provenance attestations
          - `#406 <https://github.com/ansys/grantami-recordlists/pull/406>`_

        * - Use commit shas to pin action versions
          - `#418 <https://github.com/ansys/grantami-recordlists/pull/418>`_

        * - Add integration checks completeness step at CI top-level
          - `#423 <https://github.com/ansys/grantami-recordlists/pull/423>`_

        * - Move release branch to use 25R2 release VM
          - `#425 <https://github.com/ansys/grantami-recordlists/pull/425>`_


.. vale on
