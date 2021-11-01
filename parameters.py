#!/usr/bin/env python3

######################
# Configuration
######################

# Core
AH_CORE_IP = "127.0.0.1"

AH_ORCHESTRATOR = "8441"
AH_SERVICE_REGISTRY = "8443"
AH_AUTHORIZATION = "8445"


# Cloud
CLOUD_NAME = "testcloud2"


# Systems
## Echo-server
SERVER_NAME = "echo_server"
SERVER_PASS = "123456"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 65432

## Echo-client
CLIENT_NAME = "echo_client"
CLIENT_PASS = "123456"
CLIENT_IP = "127.0.0.1"

## Auth/sysop
SYSOP_PASS = "123456"


######################
# Generated configuration
######################

CONFIG = {
    # Server
    "server_name":     # Name of the server
        SERVER_NAME,
    "server_host":     # IP address of the interface (here loopback)
        SERVER_IP,
    "server_port":     # Port to listen on (non-privileged ports are > 1023)
        SERVER_PORT,
    "server_p12_path": # Path to the p12 server certificate
        "./certificates/" + SERVER_NAME + ".p12",
    "server_p12_pass": # Password to the server certificate
        SERVER_PASS,
    "server_pub_path": # Path to the public key
        "./certificates/" + SERVER_NAME + ".pub",

    # Client
    "client_name":     # Name of the client
        CLIENT_NAME,
    "client_ip":       # IP address of the interface for the client
        CLIENT_IP,
    "client_p12_path": # Path to the p12 client certificate
        "./certificates/" + CLIENT_NAME + ".p12",
    "client_p12_pass": # Password to the client certificate
        CLIENT_PASS,
    "client_pub_path": # Path to the public key
        "./certificates/" + CLIENT_NAME + ".pub",

    # Auth/sysop
    "auth_p12_path":   # Path to the p12 sysop certificate
        "./certificates/sysop.p12",
    "auth_p12_pass":   # Password to the sysop certificate
        SYSOP_PASS,

    # Common
    "ca_path":  # Path to the CA file
        "./certificates/" + CLOUD_NAME + ".ca",
    "url_orch": # URL to the orchestrator (no endpoint)
        "https://" + AH_CORE_IP + ":" + AH_ORCHESTRATOR + "/orchestrator/",
    "url_sreg": # URL to the service registry (no endpoint)
        "https://" + AH_CORE_IP + ":" + AH_SERVICE_REGISTRY + "/serviceregistry/",
    "url_auth": # URL to the authorization (no endpoint)
        "https://" + AH_CORE_IP + ":" + AH_AUTHORIZATION + "/authorization/",
}
