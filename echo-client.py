#!/usr/bin/env python3
# Source: https://realpython.com/python-sockets/

# Socket
import socket

#HOST = '127.0.0.1'  # The server's hostname or IP address
#PORT = 65432        # The port used by the server

# Arrowhead
import requests_pkcs12

p12 = "./certificates/echo_client.p12"
pub = "./certificates/echo_client.publickey.pem"
public_key = ""

with open(pub, "r") as f:
    public_key = f.read()

public_key = "".join(public_key.split("\n")[1:-2])

url = "https://127.0.0.1:8441/orchestrator/orchestration"

# Unregister service (if registered, just to show it)
#data = {
#    "address": HOST,
#    "port": PORT,
#    "service_definition": "echo",
#    "system_name": "echoclient"
#}
#
#res = requests_pkcs12.delete(url + "unregister?" + "&".join(["%s=%s" % (key, value) for key, value in data.items()]), pkcs12_filename=p12, pkcs12_password="123456")

#print (res.text)

# Find server
data = {
    "requesterSystem": {
        "systemName": "echo_client",
        "authenticationInfo": public_key, # required with 'CERTIFICATE' and 'TOKEN'
        "address": "127.0.0.1",
        "port": 0,
    },
    "orchestrationFlags": {
        "overrideStore": "true"
    },
    "requestedService": {
        "interfaceRequirements": [ # In here, you can use 'interfaceRequirement' (string). But it is not supported by Orchestrator (anymore?).
            "HTTP-INSECURE-JSON"
        ],
        "serviceDefinitionRequirement": "echo",
    }
}

res = requests_pkcs12.post(url, json=data, pkcs12_filename=p12, pkcs12_password="123456")

print (res.status_code, res.text)

if (res.status_code >= 400):
    print ("Server not found.")
    exit (1)

for provider in res.json()["response"]:
    HOST = provider["provider"]["address"]
    PORT = provider["provider"]["port"]
    print (provider)
    break
else:
    exit (2)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

print('Received', repr(data))

