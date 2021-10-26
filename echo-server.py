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
        "interfaces": [
            "HTTP-INSECURE-JSON", # INSECURE because we do not use certificates for encrypting the data
        ],
        "providerSystem": {
            "systemName": "echo_server", # The same name as in the certificate
            "authenticationInfo": public_key, # required with 'CERTIFICATE' and 'TOKEN'
            "address": CONFIG["host"],
            "port": CONFIG["port"],
        },
        "serviceDefinition": "echo",
        "secure": "CERTIFICATE", # "NOT_SECURE", "CERTIFICATE", "TOKEN"
        "version": 1, # Who knows.
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
        "address": CONFIG["host"],
        "port": CONFIG["port"],
        "service_definition": "echo",
        "system_name": "echo_server",
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
