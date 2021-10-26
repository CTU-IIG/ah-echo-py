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
    "p12_path": # Path to the p12 certificate
        "./certificates/echo_client.p12",
    "p12_pass": # Password to the certificate
        "123456",
    "pub_path": # Path to the public key
        "./certificates/echo_client.pub",
    "url_orch": # URL to the orchestrator (no endpoint)
        "https://127.0.0.1:8441/orchestrator",
}


# Reading out the public key (as we need it in plaintext)
public_key = ""

with open(CONFIG["pub_path"], "r") as f:
    public_key = f.read()

public_key = "".join(public_key.split("\n")[1:-2])


######################
# Arrowhead Framework
######################

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
            "address": "127.0.0.1",
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
            + "/orchestration",
            json=data, pkcs12_filename=CONFIG["p12_path"], pkcs12_password=CONFIG["p12_pass"])

    print (res.status_code, res.text)

    if (res.status_code >= 400):
        print ("Server not found.", file=sys.stderr)
        return False
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
