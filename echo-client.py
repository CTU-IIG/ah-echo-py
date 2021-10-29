#!/usr/bin/env python3
# echo-client.py
"""Simple echo client that is Arrowhead Compliant."""

######################
# Imports & Globals
######################

# Arrowhead
# Requests with .p12 support
import requests_pkcs12

# Socket communication
import socket

# Error output
import sys


# Global configuration
CONFIG = {
    "ip":       # IP address of the interface for the client
        "127.0.0.1",
    "p12_path": # Path to the p12 certificate
        "./certificates/echo_client.p12",
    "p12_pass": # Password to the certificate
        "123456",
    "pub_path": # Path to the public key
        "./certificates/echo_client.pub",
    "url_orch": # URL to the orchestrator (no endpoint)
        "https://127.0.0.1:8441/orchestrator/",
    "url_sreg": # URL to the service registry (no endpoint)
        "https://127.0.0.1:8443/serviceregistry/",
}


# Reading out the public key (as we need it in plaintext)
public_key = ""

with open(CONFIG["pub_path"], "r") as f:
    public_key = f.read()

public_key = "".join(public_key.split("\n")[1:-2])


######################
# Arrowhead Framework
######################

def registerConsumer():
    """Register the client in the Arrowhead Framework."""

    print ("Registering the system...")

    data = {
        # *Who are we?
        # 'systemName': name of the client
        # 'authenticationInfo' is required with 'CERTIFICATE' and 'TOKEN'
        #   - For 'CERTIFICATE' I put there public key (so it should be asymmetric encryption).
        # 'address': IP address of the client
        # 'port': port is not used, so zero (we are consuming)
        "systemName": "echo_client",
        "authenticationInfo": public_key,
        "address": CONFIG["ip"],
        "port": 0,
    }

    res = requests_pkcs12.post(
            CONFIG["url_sreg"]
            + "register-system",
            json=data, pkcs12_filename=CONFIG["p12_path"], pkcs12_password=CONFIG["p12_pass"])

    print (res.status_code, res.text)

    if (res.status_code >= 400):
        print ("Unable to create the system.", file=sys.stderr)
        exit (1)

    print ("System registered.\nConsumer ID: %d" % res.json()["id"])

    return True


def findServer():
    """Find the echo server using Arrowhead Framework."""
    global CONFIG

    print ("Looking for echo server...")

    data = {
        # *Who are we?
        # Here we introduce the system asking the service.
        # 'systemName' should be same as the name in the certificate.
        #   - Otherwise, we get an SSL error.
        # 'authenticationInfo' is required with 'CERTIFICATE' and 'TOKEN'
        #   - For 'CERTIFICATE' I put there public key (so it should be asymmetric encryption).
        # 'address' is an IP address / name? of the system
        # 'port' is port used for the communication
        "requesterSystem": {
            "systemName": "echo_client",
            "authenticationInfo": public_key,
            "address": CONFIG["ip"],
            "port": 0, # I assume that this means that we are not listening
        },

        # Dynamic Orchestration
        #  - By passing this value we say that we want to find the counterpart dynamically,
        #  skipping any pre-set configuration in the Orchestrator.
        "orchestrationFlags": {
            "overrideStore": "true"
        },

        # Which service do we want?
        # Since the dynamic orchestration is enabled, this is mandatory*.
        "requestedService": {
            # Which interface we want to use?
            #  - This is optional.
            # In here, you can use 'interfaceRequirement' (string). But it is not supported by Orchestrator (anymore?).
            "interfaceRequirements": [
                "HTTP-INSECURE-JSON"
            ],

            # *What is the name of the service?
            "serviceDefinitionRequirement": "echo",
        }
    }

    res = requests_pkcs12.post(
            CONFIG["url_orch"]
            + "orchestration",
            json=data, pkcs12_filename=CONFIG["p12_path"], pkcs12_password=CONFIG["p12_pass"])

    print (res.status_code, res.text)

    if (res.status_code >= 400):
        print ("Client is not authorized for communication with the Orchestrator.", file=sys.stderr)

        print ("Trying to register it instead...")
        registerConsumer()

        exit (1)
    else:
        for provider in res.json()["response"]:
            CONFIG["host"] = provider["provider"]["address"]
            CONFIG["port"] = provider["provider"]["port"]
            print (provider)
            break
        else:
            return False

    return True


######################
# Echo Client
######################

def sendData():
    """Open up socket to the server, send data and obtain the response."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((CONFIG["host"], CONFIG["port"]))
        s.sendall(b'Hello, world')
        data = s.recv(1024)

    print('Received', repr(data))


######################
# Main
######################

if __name__ == "__main__":
    if findServer():
        sendData()
    else:
        print ("Unable to find the server. Is it registered and running?", file=sys.stderr)
