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
identifier_a = client.create_list(name="Example list A")

identifier_b = client.create_list(name="Example list B")
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
# -

# ## Search for the created list by name

# + tags=[]
results = client.search(SearchCriterion(name_contains="Example list B"))
print(results)
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
)
results = client.search(criterion)

print(results)
# -

# ## Search for record lists based on their items.
# We can easily search for record lists that include a specific item

# + tags=[]
criterion = SearchCriterion(contains_records=["c61e8f3a-d7e1-4b7f-8232-b2495eae6c15"])
results = client.search(criterion)

print(results)
# -


# ## Complex criterion
# Using ``BooleanCriterion``, we can build more complex queries. Here we search for lists where...
#  TODO Find an interesting complex criteria.

# + tags=[]
criterion = BooleanCriterion(
    match_any=[
        SearchCriterion(
            is_awaiting_approval=True,
            user_role=UserRole.PUBLISHER,
        ),
    ]
)

results = client.search(criterion)

print(len(results))
# -

# + tags=['hidden']
client.delete_list(identifier_a)
client.delete_list(identifier_b)
client.delete_list(identifier_c)
# -
