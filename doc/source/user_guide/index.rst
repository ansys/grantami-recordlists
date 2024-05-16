.. _ref_user_guide:

User guide
##########

Granta MI record lists
----------------------

Record lists are collections of records that can be used in any situation where it is useful to have
a persistent, server-side list of records. Records are explicitly added to a list by a user, and so
they do not need to have anything in common (as would be typical for a set of search results), and
they do not necessarily need to be in the same table or database. The user has complete flexibility
in deciding which records to add to a list.

The record list management capability is available to users in the following front-end tools:

* One MI, as **Favorites**
* The MI Materials Gateway, as **Favorites**
* This package

However, since these front-ends all share a common implementation in Granta MI, record lists can be
created, accessed, and modified in any front-end with full interoperability. The documentation in
this package is only concerned with this package. For more information about the other
tools mentioned in the preceding list, consult the :MI_docs:`Granta MI Favorites <One_MI_Favorites>`
and :MI_docs:`Granta MI Materials Gateway for Ansys Workbench <Granta_MI_MG_Help_AWB>`
documentation. Documentation is available for other Materials Gateway applications in the Ansys
Help.


Record list operations
----------------------

This package provides access to the following record list operations:

* Managing record lists, including creating, deleting, and modifying them
* Modifying the contents of a record list
* Searching for record lists based on their properties and contents
* Managing the record list lifecycle, including publishing, revising, and un-publishing record lists
* Subscribing and unsubscribing the current user to published record lists

Note that only the authenticated user can be subscribed and unsubscribed to record lists. A user
cannot subscribe or unsubscribe other users to a list on their behalf.

For examples that illustrate these operations, see :ref:`ref_grantami_recordlists_examples`. For
comprehensive information on the API, see :ref:`ref_grantami_recordlists_api_reference`.


Granta MI configuration
-----------------------

Any use of Granta MI requires the user to have permission to access the Granta MI Server. Some
record lists operations require additional permissions specific to record lists. For more
information, see the :MI_docs:`Granta MI Favorites <One_MI_Favorites>` documentation.
