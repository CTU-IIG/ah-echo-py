#!/usr/bin/env python3
# echo-server.py
"""Simple echo server that is Arrowhead Compliant."""

######################
# Imports & Globals
######################

# Arrowhead
# Requests with .p12 support
import requests_pkcs12

# Socket communication
import socket


# Global configuration
exec(open("parameters.py").read())


# Reading out the public key (as we need it in plaintext)
public_key = ""

with open(CONFIG["server_pub_path"], "r") as f:
    public_key = f.read()

public_key = "".join(public_key.split("\n")[1:-2])


######################
# Arrowhead Framework
######################

def registerService():
    """Register this service in Arrowhead Framework."""

    print ("Registering the service...")

    data = {
        # *Which interface do we use?
        # The convention (name pattern is) PROTOCOL-SECURE/INSECURE-DATA_FORMAT
        # I assume that SECURE = encrypted by the TOKEN/CERTIFICATE
        "interfaces": [
            "HTTP-INSECURE-JSON",
        ],

        # *Who are we?
        # Here we introduce the system providing the service.
        # 'systemName' should be same as the name in the certificate.
        #   - Otherwise, we get an SSL error.
        # 'authenticationInfo' is required with 'CERTIFICATE' and 'TOKEN'
        #   - For 'CERTIFICATE' I put there public key (so it should be asymmetric encryption).
        # 'address' is an IP address / name? of the server
        # 'port' is port used for the communication
        "providerSystem": {
            "systemName": CONFIG["server_name"],
            "authenticationInfo": public_key,
            "address": CONFIG["server_host"],
            "port": CONFIG["server_port"],
        },

        # *Which service we provide?
        "serviceDefinition": "echo",

        # Security info (probably just showing what can be used for authorization?)
        #  - Default is 'NOT_SECURE', other options are: 'CERTIFICATE' and 'TOKEN'
        "secure": "CERTIFICATE",

        # Version of the service
        "version": 1,

        ## Other parts we do not use (even though some of them are mandatory*):

        # *URI of the service
        # "serviceUri": "string",

        # Service is available until this UTC timestamp
        # "endOfValidity": "string",

        # Various optional metadata
        # "metadata": {
        #     "additionalProperty1": "string",
        # },
    }

    res = requests_pkcs12.post(
            CONFIG["url_sreg"]
            + "register",
            json=data, pkcs12_filename=CONFIG["server_p12_path"], pkcs12_password=CONFIG["server_p12_pass"], verify=CONFIG["ca_path"])

    print (res.status_code, res.text)

    if res.status_code < 300:
        print ("Service registered.\nInterface ID: %d\nProvider ID: %d\nService ID: %d"
            % (
                res.json()["interfaces"][0]["id"],
                res.json()["provider"]["id"],
                res.json()["serviceDefinition"]["id"],
            )
        )

    return res.status_code < 300


def unregisterService():
    """Unregister the service from the Arrowhead Framework."""

    print ("Unregistering the service...")

    data = {
        # *Who are we and what we want to unregister?
        #  - We are allowed to unregister only our services.
        # 'address': IP address of the provider
        # 'port': port of the provider
        # 'system_name': name of the provider
        "address": CONFIG["server_host"],
        "port": CONFIG["server_port"],
        "system_name": CONFIG["server_name"],

        # *'service_definition': service to be removed
        "service_definition": "echo",
    }

    res = requests_pkcs12.delete(
            CONFIG["url_sreg"]
            + "unregister?"
            + "&".join(
                ["%s=%s" % (key, value) for key, value in data.items()]
            ), pkcs12_filename=CONFIG["server_p12_path"], pkcs12_password=CONFIG["server_p12_pass"], verify=CONFIG["ca_path"])

    print (res.status_code, res.text)


######################
# Echo Server
######################

def setupSocket():
    """Setup the socket and open up the communication.

    Source:
    https://realpython.com/python-sockets/
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((CONFIG["server_host"], CONFIG["server_port"]))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)


######################
# Main
######################

if __name__ == "__main__":
    if registerService():
        try:
            setupSocket()
        except:
            pass
        finally:
            unregisterService()
    else:
        print ("Unable to register the service. Trying to unregister it instead.")
        unregisterService()
