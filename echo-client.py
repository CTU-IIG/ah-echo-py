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
exec(open("parameters.py").read())


# Reading out the public key (as we need it in plaintext)
public_key = ""

with open(CONFIG["client_pub_path"], "r") as f:
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
        "systemName": CONFIG["client_name"],
        "authenticationInfo": public_key,
        "address": CONFIG["client_ip"],
        "port": 0,
    }

    res = requests_pkcs12.post(
            CONFIG["url_sreg"]
            + "register-system",
            json=data, pkcs12_filename=CONFIG["client_p12_path"], pkcs12_password=CONFIG["client_p12_pass"], verify=CONFIG["ca_path"])

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
            "systemName": CONFIG["client_name"],
            "authenticationInfo": public_key,
            "address": CONFIG["client_ip"],
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
            json=data, pkcs12_filename=CONFIG["client_p12_path"], pkcs12_password=CONFIG["client_p12_pass"], verify=CONFIG["ca_path"])

    print (res.status_code, res.text)

    if (res.status_code >= 400):
        print ("Client is not authorized for communication with the Orchestrator.", file=sys.stderr)

        print ("Trying to register it instead...")
        registerConsumer()

        exit (1)
    else:
        for provider in res.json()["response"]:
            CONFIG["client_host"] = provider["provider"]["address"]
            CONFIG["client_port"] = provider["provider"]["port"]
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
        s.connect((CONFIG["client_host"], CONFIG["client_port"]))
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
