import Client, App, Utility

logs = Utility.Logger()

logs.log("", "", Utility.LogType.Type.CLEAR)

client = Client.ClientSide('CLIENT')

client._start()
App.server._start()
client._set_peer('127.0.0.1', App._get_inc_port())
App._set_out_peer(client.incoming_port_)

print(f"Inc port {App.server.incoming_port_}")
print(f"Out port {App.server.outgoing_port_}")

print(f"Inc port {client.incoming_port_}")
print(f"Out port {client.outgoing_port_}")

App._run_app()