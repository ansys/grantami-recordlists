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
# This notebook demonstrates how to search for record lists, using ``SearchCriterion`` and
# ``BooleanCriterion``.

# .. note:: Running this notebook requires permissions to request publication, publish and revise a
# list.

# ## Connect to Granta MI

# + tags=[]
from ansys.grantami.recordlists import Connection
from ansys.grantami.recordlists.models import (
    BooleanCriterion,
    RecordListItem,
    SearchCriterion,
    UserRole,
)

connection = Connection("http://my_grantami_server/mi_servicelayer").with_autologon()
client = connection.connect()
# -

# ## Create some lists to search on

# + tags=[]
identifier_a = client.create_list(name="Approved materials - Metals")
client.request_approval(identifier_a)
client.publish(identifier_a)

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
client.request_approval(identifier_b)
client.publish(identifier_b)

identifier_c = client.revise_list(identifier_b)
identifier_d = client.create_list(name="My personal list")
# -

# ## Search for a list by name

# + tags=[]
results = client.search(SearchCriterion(name_contains="Approved materials - Ceramics"))
results
# -

# ## Search for 'personal' record lists.
# A 'personal' record list is not published, is not awaiting approval, and is not a revision of
# another list. It is simply a list, that the current user has created for their own use.
# We'll also exclude internal lists, created by other Granta MI applications.

# + tags=[]
criterion = SearchCriterion(
    is_published=False,
    is_revision=False,
    is_awaiting_approval=False,
    is_internal_use=False,
    user_role=UserRole.OWNER,
)
results = client.search(criterion)
results
# -

# ## Search for record lists based on their items.
# We can easily search for record lists that include a specific item

# + tags=[]
criterion = SearchCriterion(contains_records=["c61e8f3a-d7e1-4b7f-8232-b2495eae6c15"])
results = client.search(criterion)
results
# -


# ## Complex criterion
# Using ``BooleanCriterion``, we can build complex queries. Here we search for published lists
# following the naming convention "Approved materials - {Material family}" and specifically,
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
results = client.search(criterion)
results
# -

# + nbsphinx="hidden"
client.delete_list(identifier_a)
client.delete_list(identifier_b)
client.delete_list(identifier_c)
client.delete_list(identifier_d)
# -
