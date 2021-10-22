#!/usr/bin/env python3
# Setup the rules for Echo test

import json

# Arrowhead
import requests_pkcs12

p12 = "./certificates/sysop.p12"
pub = "./certificates/sysop.pub"
client_pub = "./certificates/echo_client.publickey.pem"
server_pub = "./certificates/echo_server.publickey.pem"
public_key = ""

with open(pub, "r") as f:
    public_key = f.read()

public_key = "".join(public_key.split("\n")[1:-2])

client_public_key = ""

with open(client_pub, "r") as f:
    client_public_key = f.read()

client_public_key = "".join(client_public_key.split("\n")[1:-2])

server_public_key = ""

with open(server_pub, "r") as f:
    server_public_key = f.read()

server_public_key = "".join(server_public_key.split("\n")[1:-2])


url = "https://127.0.0.1:8443/serviceregistry/"
auth_url = "https://127.0.0.1:8445/authorization/"
orch_url = "https://127.0.0.1:8441/orchestrator/"

# Register provider system
providerID = -1

data = {
    "systemName": "echo_server",
    "authenticationInfo": server_public_key, # required with 'CERTIFICATE' and 'TOKEN'
    "address": "127.0.0.1",
    "port": 65432,
}

res = requests_pkcs12.post(url + "mgmt/systems", json=data, pkcs12_filename=p12, pkcs12_password="123456")

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(url + "mgmt/systems", pkcs12_filename=p12, pkcs12_password="123456")

    print (res.status_code, res.text)

    for system in res.json()["data"]:
        if system["systemName"] == data["systemName"]:
            providerID = system["id"]

else:
   providerID = res.json()["id"]


print ("Provider ID: %d" % providerID)

# Register consumer system
consumerID = -1

data = {
    "systemName": "echo_client",
    "authenticationInfo": client_public_key, # required with 'CERTIFICATE' and 'TOKEN'
    "address": "127.0.0.1",
    "port": 0,
}

res = requests_pkcs12.post(url + "mgmt/systems", json=data, pkcs12_filename=p12, pkcs12_password="123456")

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(url + "mgmt/systems", pkcs12_filename=p12, pkcs12_password="123456")

    print (res.status_code, res.text)

    for system in res.json()["data"]:
        if system["systemName"] == data["systemName"]:
            consumerID = system["id"]
            break

else:
    consumerID = res.json()["id"]


print ("Consumer ID: %d" % consumerID)


# Define service
serviceID = -1
providerIDs = []

data = {
    "serviceDefinition": "echo",
}

res = requests_pkcs12.post(url + "mgmt/services", json=data, pkcs12_filename=p12, pkcs12_password="123456")

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(url + "mgmt/servicedef/" + data["serviceDefinition"], pkcs12_filename=p12, pkcs12_password="123456")

    print (res.status_code, res.text)

    serviceID = res.json()["data"][0]["serviceDefinition"]["id"]

    # Note: This returns even the providers!
    for providers in res.json()["data"]:
        providerIDs.append(providers["provider"]["id"])

else:
    serviceID = res.json()["id"]


print ("Service ID: %d" % serviceID)


# Define interface
interfaceID = -1

data = {
    "interfaceName": "HTTP-INSECURE-JSON",
}

res = requests_pkcs12.post(url + "mgmt/interfaces", json=data, pkcs12_filename=p12, pkcs12_password="123456")

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(url + "mgmt/interfaces", pkcs12_filename=p12, pkcs12_password="123456")

    print (res.status_code, res.text)

    for interface in res.json()["data"]:
        print (interface)
        if interface["interfaceName"] == data["interfaceName"]:
            interfaceID = interface["id"]
            break

else:
    interfaceID = res.json()["id"]


print ("Interface ID: %d" % interfaceID)


# Authorize connection between client and server
data = {
    "consumerId": consumerID,
    "interfaceIds": [
        interfaceID,
    ],
    #"providerIds": providerIDs, # More dynamic solution
    "providerIds": [
        providerID,
    ],
    "serviceDefinitionIds": [
        serviceID,
    ],
}

res = requests_pkcs12.post(auth_url + "mgmt/intracloud", json=data, pkcs12_filename=p12, pkcs12_password="123456")

print (res.status_code, res.text)


# Add orchestration rule between client and server
data = {
    "consumerSystemId": consumerID,
    "providerSystem": {
    
    }}
