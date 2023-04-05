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

# # Getting started
# This example shows how to connect to Granta MI and perform basic operations on record lists.

# ## Connect to Granta MI

# First, use the ``ansys.grantami.recordlists.Connection`` class to connect to the Granta MI
# server. The ``Connection`` class uses a fluent interface to build the connection, which is
# always invoked in the following sequence:
#
# 1. Specify your Granta MI Service Layer URL as a parameter to the ``Connection`` class.
# 2. Specify the authentication method using a ``Connection.with_...()`` method.
# 3. Use the ``Connection.connect()`` method to finalize the connection.
#
# This returns a client object, called ``client`` in these examples.

# + tags=[]
from ansys.grantami.recordlists import Connection, RecordListItem

connection = Connection("http://my_grantami_server/mi_servicelayer").with_autologon()
client = connection.connect()
# -

# ## Create a new record list
# API operations expect a ``RecordList`` instance as input. For the purpose of this example, create
# a new record list, using the ``create_list`` method. It returns a ``RecordList`` instance.

# + tags=[]
example_list = client.create_list(
    name="Example list",
    description=f"Created by example 00_Basic_usage",
)
example_list
# -

# ## Get the details of an existing record list
# The ``get_list`` method allows obtaining a ``RecordList`` instance from an existing record list
# unique identifier.

# + tags=[]
list_details = client.get_list(example_list.identifier)
list_details
# -

# + tags=[]
print(f"Name: {list_details.name}")
print(f"Identifier: {list_details.identifier}")
print(f"Notes: {list_details.notes}")
print(f"Description: {list_details.description}")
print(f"Created timestamp: {list_details.created_timestamp}")
# -

# ## Get all record lists

# + tags=[]
all_lists = client.get_all_lists()
all_lists
# -

# ## Copy a record list

# + tags=[]
list_copy = client.copy_list(example_list)
list_copy
# -

# ## Update a record list

# + tags=[]
updated_list_copy = client.update_list(
    list_copy,
    name="Copied - Example List",
    description=None,
    notes="Copy of the example list",
)
print(f"Name: {updated_list_copy.name}")
print(f"Identifier: {updated_list_copy.identifier}")
print(f"Notes: {updated_list_copy.notes}")
print(f"Description: {updated_list_copy.description}")
print(f"Created timestamp: {updated_list_copy.created_timestamp}")
# -

# ## Delete a record list

# + tags=[]
client.delete_list(updated_list_copy)
# -

# ## Read the items in a record list
# The list was created at the beginning of this example, so the list is currently empty.

# + tags=[]
items = client.get_list_items(example_list)
items
# -

# ## Add items to a record list
# Add items to a list using ``add_items_to_list``.
# Items are described using the database GUID, table GUID, and record history GUID.

# + tags=[]
client.add_items_to_list(
    example_list,
    items=[
        RecordListItem(
            database_guid="e595fe23-b450-4d18-8c08-4a0f378ef095",
            table_guid="81dff531-0254-4fbe-9621-174b10aaee3d",
            record_history_guid="3bc2b82f-0199-4f3b-a7af-8d520250b180",
        ),
    ],
)
# -

# Then retrieve the items and confirm that the record list now includes the added items.

# + tags=[]
list_items = client.get_list_items(example_list)
list_items
# -

# ## Remove items from a record list
# Remove items from a record list using ``remove_items_from_list``.

# + tags=[]
client.remove_items_from_list(
    example_list,
    items=list_items,
)
# -

# Then retrieve the items again and confirm that the record list is empty.

# + tags=[]
items = client.get_list_items(example_list)
items
# -


# + nbsphinx="hidden"
client.delete_list(example_list)
# -
