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
CONFIG = {
    "host":     # IP address of the interface (here loopback)
        "127.0.0.1",
    "port":     # Port to listen on (non-privileged ports are > 1023)
         65432,
    "p12_path": # Path to the p12 certificate
        "./certificates/echo_server.p12",
    "p12_pass": # Password to the certificate
        "123456",
    "pub_path": # Path to the public key
        "./certificates/echo_server.pub",
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
            "systemName": "echo_server",
            "authenticationInfo": public_key,
            "address": CONFIG["host"],
            "port": CONFIG["port"],
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
            json=data, pkcs12_filename=CONFIG["p12_path"], pkcs12_password=CONFIG["p12_pass"])

    print (res.status_code, res.text)

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
        "address": CONFIG["host"],
        "port": CONFIG["port"],
        "system_name": "echo_server",

        # *'service_definition': service to be removed
        "service_definition": "echo",
    }

    res = requests_pkcs12.delete(
            CONFIG["url_sreg"]
            + "unregister?"
            + "&".join(
                ["%s=%s" % (key, value) for key, value in data.items()]
            ), pkcs12_filename=CONFIG["p12_path"], pkcs12_password=CONFIG["p12_pass"])

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
        s.bind((CONFIG["host"], CONFIG["port"]))
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
