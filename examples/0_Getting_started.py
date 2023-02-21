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
# ## Connect to Granta MI

# + tags=[]
from ansys.grantami.recordlists import Connection

connection = Connection("http://my_grantami_server/mi_servicelayer").with_autologon()
client = connection.connect()
# -

# ## Create a new list

# + tags=[]
new_list = client.create_list(name="Example list", description=f"Created with {__name__}")

new_list
# -
