#!/usr/bin/env python3
# echo-auth.py
"""Script for adding an authorization rule between echo server and client."""

######################
# Imports & Globals
######################

# Arrowhead
# Requests with .p12 support
import requests_pkcs12

# Error output
import sys

# Argument parsing
import argparse


# Global configuration
exec(open("parameters.py").read())


######################
# Arrowhead Framework
######################

def addAuthorizationRule(consumerID, interfaceID, providerID, serviceID):
    """Add an authorization rule between echo client and echo server.

    Return:
    True when successful
    """

    print ("Adding the authorization rule...")

    # Authorize connection between client and server
    data = {
        "consumerId": consumerID,
        "interfaceIds": [
            interfaceID,
        ],
        "providerIds": [
            providerID,
        ],
        "serviceDefinitionIds": [
            serviceID,
        ],
    }

    res = requests_pkcs12.post(
            CONFIG["url_auth"]
            + "mgmt/intracloud",
            json=data, pkcs12_filename=CONFIG["auth_p12_path"], pkcs12_password=CONFIG["auth_p12_pass"])

    print (res.status_code, res.text)

    return res.status_code < 400


######################
# Main
######################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script used for authorizing echo client and echo server communication.")

    parser.add_argument("-c", type=int, required=True, metavar="consumerID",
                        help="ID of the consumer system")
    parser.add_argument("-i", type=int, required=True, metavar="interfaceID",
                        help="ID of the used interface")
    parser.add_argument("-p", type=int, required=True, metavar="providerID",
                        help="ID of the provider system")
    parser.add_argument("-s", type=int, required=True, metavar="serviceID",
                        help="ID of the service")

    args = parser.parse_args()

    if not addAuthorizationRule(args.c, args.i, args.p, args.s):
        print ("Unable add the intracloud rule.", file=sys.stderr)
