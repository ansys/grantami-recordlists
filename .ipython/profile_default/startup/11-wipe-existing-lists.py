from ansys.grantami.recordlists import Connection

# Connect using autologon, credentials are monkeypatched already
client = Connection("http://my_grantami_server/mi_servicelayer").with_autologon().connect()

all_lists = client.get_all_lists()
for rl in all_lists:
    client.delete_list(rl.identifier)
