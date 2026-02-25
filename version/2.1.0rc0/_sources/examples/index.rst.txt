.. _ref_grantami_recordlists_examples:

Examples
========

The following examples demonstrate key aspects of PyGranta RecordLists.

To run these examples, install dependencies with this command:

.. code::

   pip install ansys-grantami-recordlists[examples]

And launch ``jupyterlab`` with this command:

.. code::

   jupyter lab


.. jinja:: examples

    {% if build_examples %}

    .. toctree::
       :maxdepth: 2

       00_basic_usage
       01_publishing_revising_withdrawing
       02_searching

    {% else %}

    .. toctree::
       :maxdepth: 2

       test_example

    {% endif %}


Users of the Granta MI Scripting Toolkit can find an example of interoperability in the Granta MI Scripting Toolkit
documentation.
