#!/usr/bin/env python3
# Echo Server
# Source: https://realpython.com/python-sockets/

######################
# Imports & Globals
######################

# Arrowhead
## Requests with .p12 support
import requests_pkcs12

# Socket communication
import socket


# Global variables
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
p12 = "./certificates/echo_server.p12"
pub = "./certificates/echo_server.publickey.pem"
url = "https://127.0.0.1:8443/serviceregistry/"


# Reading out the public key (as we need it in plaintext)
public_key = ""

with open(pub, "r") as f:
    public_key = f.read()

public_key = "".join(public_key.split("\n")[1:-2])


######################
# Arrowhead Framework
######################

# Register service
data = {
    "interfaces": [
        "HTTP-INSECURE-JSON",
    ],
    "providerSystem": {
        "systemName": "echo_server", # PREMCompiler
        "authenticationInfo": public_key, # required with 'CERTIFICATE' and 'TOKEN'
        "address": HOST,
        "port": PORT,
    },
    "serviceDefinition": "echo",
    "secure": "CERTIFICATE", # "NOT_SECURE", "CERTIFICATE", "TOKEN"
    "version": 1, # Who knows.
}

res = requests_pkcs12.post(url + "register", json=data, pkcs12_filename=p12, pkcs12_password="123456")

print (res.text)


######################
# Echo Server
######################

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
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
except:
    pass
finally:
    # Unregister the service
    data = {
        "address": HOST,
        "port": PORT,
        "service_definition": "echo",
        "system_name": "echo_server"
    }

    res = requests_pkcs12.delete(url + "unregister?" + "&".join(["%s=%s" % (key, value) for key, value in data.items()]), pkcs12_filename=p12, pkcs12_password="123456")

    print (res.text)
