# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Searching
# This notebook demonstrates how to search for record lists using ``SearchCriterion`` and ``BooleanCriterion``.

# .. note:: Running this notebook requires permissions to request publication of, to publish, and to revise a
# record list. Contact your Granta MI administrator for more information.

# ## Connect to Granta MI and create a record list

# Import the ``Connection`` class and create the connection. See the [Basic usage](00_Basic_usage.ipynb)
# example for more details.

# + tags=[]
from ansys.grantami.recordlists import (
    BooleanCriterion,
    Connection,
    RecordListItem,
    SearchCriterion,
    UserRole,
)

connection = Connection("http://my_grantami_server/mi_servicelayer").with_autologon()
client = connection.connect()
# -

# Create some record lists for use in this example:
#
# * ``identifier_a``: Published, empty
# * ``identifier_b``: Published, populated
# * ``identifier_c``: Revision of ``identifier_b``
# * ``identifier_d``: Unpublished
#
# See the [Publishing, revising, and withdrawing record lists](01_Publishing_revising_withdrawing.ipynb)
# example for more details.

# + tags=[]
identifier_a = client.create_list(name="Approved materials - Metals")
client.request_list_approval(identifier_a)
client.publish_list(identifier_a)

identifier_b = client.create_list(name="Approved materials - Ceramics")
client.add_items_to_list(
    identifier_b,
    items=[
        RecordListItem(
            "9716c5a3-da85-4126-a922-3fbb854656d8",
            "d352fd12-c342-41c1-9da7-dac0dac1c6d9",
            "c61e8f3a-d7e1-4b7f-8232-b2495eae6c15",
        )
    ],
)
client.request_list_approval(identifier_b)
client.publish_list(identifier_b)

identifier_c = client.revise_list(identifier_b)
identifier_d = client.create_list(name="My personal list")
# -

# ## Search for a record list by name

# Use the `name_contains` keyword argument for the ``SearchCriterion`` constructor to specify
# a search criterion based on the record list name.

# + tags=[]
results = client.search_for_lists(SearchCriterion(name_contains="Approved materials - Ceramics"))
results
# -

# ## Search for 'personal' record lists
# A 'personal' record list is a list that the current user has created for their own use. It is
# owned by the current user, is not published, is not awaiting approval, and is not a revision of another list.
# Lists are generally in this state if they are created in the Favorites or Explore apps and are not submitted
# for publication.

# To search for a list of this type, use the ``SearchCriterion`` below (``is_internal_use=False`` excludes
# record lists created by other Granta MI applications for internal operations).

# + tags=[]
criterion = SearchCriterion(
    is_published=False,
    is_revision=False,
    is_awaiting_approval=False,
    is_internal_use=False,
    user_role=UserRole.OWNER,
)
results = client.search_for_lists(criterion)
results
# -

# ## Search for a record list by contents
# Search for record lists that contain a specific record with the ``contains_records`` keyword.
# Specifying ``include_items=True`` when calling ``search_for_lists`` will populate ``items`` on the results.

# + tags=[]
criterion = SearchCriterion(contains_records=["c61e8f3a-d7e1-4b7f-8232-b2495eae6c15"])
results = client.search_for_lists(criterion, include_items=True)
results
# -

# + tags=[]
results[0].items
# -


# ## Search using a complex criterion
# Build complex queries with ``BooleanCriterion``. For example, search for published record lists
# following the naming convention "Approved materials - {Material family}", but specifically only
# metals and ceramics.

# + tags=[]
criterion = BooleanCriterion(
    match_all=[
        SearchCriterion(
            name_contains="Approved materials",
            is_published=True,
        ),
        BooleanCriterion(
            match_any=[
                SearchCriterion(
                    name_contains="Metals",
                ),
                SearchCriterion(
                    name_contains="Ceramics",
                ),
            ]
        ),
    ]
)
results = client.search_for_lists(criterion)
results
# -

# + nbsphinx="hidden"
client.delete_list(identifier_a)
client.delete_list(identifier_b)
client.delete_list(identifier_c)
client.delete_list(identifier_d)
# -
