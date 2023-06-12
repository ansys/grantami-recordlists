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

# # Publishing, revising, and withdrawing record lists
# This example shows how to connect to Granta MI and perform advanced operations on record lists,
# such as publishing, withdrawing, and revising a list. For more information about the concepts
# discussed here, see the Help in the Granta MI Favorites app.

# .. note:: Running this notebook requires permissions to request publication of, to publish, and to
# revise a record list. Contact your Granta MI administrator for more information.

# ## Connect to Granta MI and create a record list

# Import the ``Connection`` class and create the connection. See the
# [Getting started](00_Basic_usage.ipynb) example for more details.

# + tags=[]
from ansys.grantami.recordlists import Connection

connection = Connection("http://my_grantami_server/mi_servicelayer").with_autologon()
client = connection.connect()
# -

# Create a record list for use in this example.

# + tags=[]
example_list = client.create_list(
    name="Example list",
    description=f"Created by example 01_Advanced_usage",
)
example_list
# -

# Record lists include two properties describing two aspects of their status: whether they are
# awaiting approval to be published, and whether they are currently published.
# Define a function to display the status properties.


# + tags=[]
def print_status(record_list):
    print(f"Awaiting approval: {record_list.awaiting_approval}")
    print(f"Published: {record_list.published}")


print_status(example_list)
# -

# ## Publish a record list

# A record list is proposed for publication by calling the ``request_list_approval`` method with the
# record list to be published.

# + tags=[]
updated_list = client.request_list_approval(example_list)

print_status(updated_list)
# -

# Publish the record list by using the ``publish_list`` method.

# + tags=[]
updated_list = client.publish_list(example_list)

print_status(updated_list)
# -

# ## Revise a record list

# A published record list cannot be modified directly. Instead, first create a revision of the
# published record list using the ``revise_list`` method. This creates an editable copy of the
# original record list (a list revision), and leaves the original record list unchanged.

# + tags=[]
revision_list = client.revise_list(example_list)

print_status(revision_list)
# -

# The record list revision includes a property tracking the parent record list:

# + tags=[]
print(f"Is revision: {revision_list.is_revision}")
print(f"Parent identifier: {revision_list.parent_record_list_identifier}")
# -

# Modifications made to the list revision are applied to the original list when the list revision
# is published. Once the original list is updated, the list revision is deleted and is no longer
# available.

# + tags=[]
updated_revision_list = client.update_list(revision_list, notes="Added during revision process")
updated_revision_list = client.request_list_approval(updated_revision_list)
updated_original_list = client.publish_list(updated_revision_list)

# When publishing a revision list, the returned object is the updated parent list.
# Check the notes of the list to confirm the revisions were made successfully.
print(f"Notes: {updated_original_list.notes}")
print(f"Is published: {updated_original_list.published}")
# -

# ## Withdraw a record list
# When a record list is in the published state, calling ``request_list_approval`` requests the
# withdrawal of that list.

# + tags=[]
updated_list = client.request_list_approval(example_list)

print_status(updated_list)
# -

# Use the ``unpublish_list`` method to withdraw a record list.

# + tags=[]
updated_list = client.unpublish_list(example_list)

print_status(updated_list)
# -

# + nbsphinx="hidden"
client.delete_list(example_list)
# -
