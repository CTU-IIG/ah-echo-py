#!/usr/bin/env python3
# echo-setup.py
"""Setup the rules for Echo test. Run from localhost."""

######################
# Imports & Globals
######################

# Arrowhead
# Requests with .p12 support
import requests_pkcs12


# Global configuration
exec(open("parameters.py").read())


client_public_key = ""

with open(CONFIG["client_pub_path"], "r") as f:
    client_public_key = f.read()

client_public_key = "".join(client_public_key.split("\n")[1:-2])

server_public_key = ""

with open(CONFIG["server_pub_path"], "r") as f:
    server_public_key = f.read()

server_public_key = "".join(server_public_key.split("\n")[1:-2])


######################
# Arrowhead Framework
######################

# Register provider system
providerID = -1

data = {
    "systemName": CONFIG["server_name"],
    "authenticationInfo": server_public_key, # required with 'CERTIFICATE' and 'TOKEN'
    "address": CONFIG["server_host"],
    "port": CONFIG["server_port"],
}

res = requests_pkcs12.post(CONFIG["url_sreg"] + "mgmt/systems", json=data, pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(CONFIG["url_sreg"] + "mgmt/systems", pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

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
    "systemName": CONFIG["client_name"],
    "authenticationInfo": client_public_key, # required with 'CERTIFICATE' and 'TOKEN'
    "address": CONFIG["client_ip"],
    "port": 0,
}

res = requests_pkcs12.post(CONFIG["url_sreg"] + "mgmt/systems", json=data, pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(CONFIG["url_sreg"] + "mgmt/systems", pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

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

res = requests_pkcs12.post(CONFIG["url_sreg"] + "mgmt/services", json=data, pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(CONFIG["url_sreg"] + "mgmt/servicedef/" + data["serviceDefinition"], pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

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

res = requests_pkcs12.post(CONFIG["url_sreg"] + "mgmt/interfaces", json=data, pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

print (res.status_code, res.text)

if (res.status_code >= 400):
    res = requests_pkcs12.get(CONFIG["url_sreg"] + "mgmt/interfaces", pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

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

res = requests_pkcs12.post(CONFIG["url_auth"] + "mgmt/intracloud", json=data, pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

print (res.status_code, res.text)

