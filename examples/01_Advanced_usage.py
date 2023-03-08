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

# # Advanced usage
# This example shows how to connect to Granta MI and perform advanced operations on record lists,
# such as publishing, withdrawing, revising a list.

# + tags=[]
from ansys.grantami.recordlists import Connection

connection = Connection("http://my_grantami_server/mi_servicelayer").with_autologon()
client = connection.connect()
# -

# + tags=[]
list_identifier = client.create_list(
    name="Example list",
    description=f"Created by example 01_Advanced_usage",
)
list_identifier
# -

# Record lists include properties describing their current status: whether they are published or
# awaiting approval.
# We define a function to retrieve the details of a list and print its statuses.

# + tags=[]
def print_status(identifier):
    list_details = client.get_list(identifier)
    print(f"Awaiting approval: {list_details.awaiting_approval}")
    print(f"Published: {list_details.published}")


print_status(list_identifier)
# -

# ## Requesting publication

# + tags=[]
client.request_list_approval(list_identifier)

print_status(list_identifier)
# -

# ## Publishing
# A published list cannot be modified. To update a published list, one can create a revision of it.

# + tags=[]
client.publish_list(list_identifier)

print_status(list_identifier)
# -

# ## Revising a list

# ### Creating a list revision
# Revising a record list creates a copy of the original list, on which modifications can be made.
# + tags=[]
revision_identifier = client.revise_list(list_identifier)

print_status(list_identifier)
# -

# The original list is unchanged. The revision list includes a property tracking the parent list:

# + tags=[]
revision_details = client.get_list(revision_identifier)

print(f"Is revision: {revision_details.is_revision}")
print(f"Parent identifier: {revision_details.parent_record_list_identifier}")
# -

# ### Updating a published list
# Modifications made to the revision list will be applied to the original list when the revision
# list is published. At this point, the revision list will also be deleted.

# + tags=[]
updated_revision_list = client.update_list(
    revision_identifier, notes="Added during revision process"
)
client.request_list_approval(revision_identifier)
client.publish_list(revision_identifier)

# Checking the notes of the original list
list_details = client.get_list(list_identifier)
print(f"Notes: {list_details.notes}")
print(f"Is published: {list_details.published}")
# -

# ## Requesting withdrawal
# When a list is already published, calling `request_list_approval` is equivalent to requesting
# the withdrawal of the list.

# + tags=[]
client.request_list_approval(list_identifier)

print_status(list_identifier)
# -

# ## Withdrawing

# + tags=[]
client.unpublish_list(list_identifier)

print_status(list_identifier)
# -

# + nbsphinx="hidden"
client.delete_list(list_identifier)
# -
