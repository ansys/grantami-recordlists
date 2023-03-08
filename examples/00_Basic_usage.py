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

# # Basic usage
# This example shows how to connect to Granta MI and perform basic operations on record lists.

# ## Connect to Granta MI

# + tags=[]
from ansys.grantami.recordlists import Connection, RecordListItem

connection = Connection("http://my_grantami_server/mi_servicelayer").with_autologon()
client = connection.connect()
# -

# ## CRUD operations
# ### Creating a new list

# + tags=[]
list_identifier = client.create_list(
    name="Example list",
    description=f"Created by example 00_Basic_usage",
)
list_identifier
# -

# ### Getting details of a record list

# + tags=[]
list_details = client.get_list(list_identifier)
list_details
# -

# + tags=[]
print(list_details.name)
print(list_details.identifier)
print(list_details.notes)
print(list_details.description)
print(list_details.created_timestamp)
# -

# ### Getting all record lists

# + tags=[]
all_lists = client.get_all_lists()
all_lists
# -

# ### Copying a record list

# + tags=[]
copied_list_identifier = client.copy_list(list_identifier)
copied_list_identifier
# -

# ### Updating a record list

# + tags=[]
copied_list_details = client.update_list(
    copied_list_identifier,
    name="Copied - Example List",
    description=None,
    notes="Copy of the example list",
)
print(copied_list_details.name)
print(copied_list_details.identifier)
print(copied_list_details.description)
print(copied_list_details.notes)
# -

# ### Deleting a record list

# + tags=[]
client.delete_list(copied_list_identifier)
# -

# ## Managing record list items
# ### Read items of a record list
# We have just created the record list. We can get its items and confirm that there aren't any.

# + tags=[]
items = client.get_list_items(list_identifier)
items
# -

# ### Add items to a record list
# One can add items to a list, using `add_items_to_list`.
# Items are described using the database GUID, table GUID, and record history GUID.
# We then retrieve the items again, and confirm that the list now includes the added items.

# + tags=[]
client.add_items_to_list(
    list_identifier,
    items=[
        RecordListItem(
            database_guid="e595fe23-b450-4d18-8c08-4a0f378ef095",
            table_guid="81dff531-0254-4fbe-9621-174b10aaee3d",
            record_history_guid="3bc2b82f-0199-4f3b-a7af-8d520250b180",
        ),
    ],
)
list_items = client.get_list_items(list_identifier)
list_items
# -

# ### Remove items from a record list
# One can remove items from a list, using `remove_items_from_list`.
# We then retrieve the items again, and confirm that the list has no items anymore.

# + tags=[]
client.remove_items_from_list(
    list_identifier,
    items=list_items,
)
items = client.get_list_items(list_identifier)
items
# -


# + nbsphinx="hidden"
client.delete_list(list_identifier)
# -
