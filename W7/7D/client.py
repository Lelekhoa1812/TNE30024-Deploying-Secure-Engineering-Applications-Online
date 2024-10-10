"""
TCP Echo Client Program

Connects to a TCP Echo Server and sends user text to server, prints responses to screen. User must specify the server
to connect to

  usage: client.py [-h] [-p PORT] [-v VALIDATE_CLIENT VALIDATE_CLIENT] server cert

  TCP Echo Client

  positional arguments:
    server                Name of server to connect to

  options:
    -h, --help            show this help message and exit
    -p PORT, --port PORT  Port number to run the TLS echo server on (default=1024)options:

Written by Jason But
Copyright 2024
"""
import os

import socket

import argparse

import ssl # ADD!
from datetime import datetime  # ADD! Add for date parsing

class IntRange:
    """
    class IntRange

    Class to allow an integer only in the provided range. Used to limit allowable options on CLI
    """

    def __init__(self, imin, imax):
        """
        Constructor - Internally store min and max values integer can take
        :param imin: Minimum integer in range
        :param imax: Maximum integer in range
        """
        self.imin = imin
        self.imax = imax

    def __call__(self, arg):
        """
        Validate integer
        :param arg: If arg is not an integer or value is outside allowed range, raise an exception for the ArgParse to handle
        """
        try:
            value = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Must be an integer in the range [{self.imin}, {self.imax}]")
        if (value < self.imin) or (value > self.imax):
            raise argparse.ArgumentTypeError(f"Must be an integer in the range [{self.imin}, {self.imax}]")
        return value


class ValidFile:
    """
    class ValidFile

    Class to check that the provided command line parameter specifies an existing file on the system

    NOTE: This class not used here, can be used when extending the parser to ensure provided parameter is a file that exists
    """

    def __call__(self, arg) -> str:
        """
        Validate that provided value nominates an existing file
        :param arg: String containing filename
        :return: Raise exception on failure otherwise return filename
        """
        if not os.path.exists(arg):
            raise argparse.ArgumentTypeError(f'Nominated file "{arg}" does not exist')
        return arg


def parse_cli():
    """
    Create a command line parser to parse command line options
    :return: parsed arguments
    """
    parser = argparse.ArgumentParser(description='TCP Echo Client', formatter_class=argparse.RawTextHelpFormatter, allow_abbrev=False)
 
    parser.add_argument('server', help='Name of server to connect to')

    # Uncomment the line below to add options for Lab 6 allowing specification of server certificate, and optionally server commonname
    parser.add_argument('cert', type=ValidFile(), help='Location of Server Public Certificate File to use to validate server')
    parser.add_argument('-c', '--common_name', help="Common Name of server certificate if it is different than server as listed above")

    parser.add_argument('key', type=ValidFile(), help='Location of Client Private Key File')

    parser.add_argument('cafile', type=ValidFile(), help='Location of Root CA File')

    parser.add_argument('-p', '--port', type=IntRange(1024, 16384), default=1024, help='Port number to run the TLS echo server on (default=1024)')

    # Uncomment the line below to add options for Lab 7 allowing specification of Client certificate and key to use to validate client to server
    parser.add_argument('-v', '--validate_client', nargs=2, type=ValidFile(), help='Location of Certificate File to use to validate client to server. First file is the Public Client Certificate, the second is the Private Client Key')

    return parser.parse_args()

def run_client(server_addr, port, certfile, keyfile, cafile):
    """
    Run the TLS client with mutual authentication.
    :param server_addr: Server address to connect to
    :param certfile: Client certificate file (full chain)
    :param keyfile: Client private key file
    :param cafile: Root CA file to verify server certificate
    """
    # Create SSL context for client, specifying the CA root certificate
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
    
    # Load the client certificate and key
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    
    try:
        with socket.create_connection((server_addr, port)) as sock:
            with context.wrap_socket(sock, server_hostname=server_addr) as sslsock:
                print(f"TLS connection established to {server_addr}")
                cert = sslsock.getpeercert()
                print_cert_details(cert)
                msg = input("Message to send: ")
                if msg:
                    sslsock.send(msg.encode('utf-8'))
                    data = sslsock.recv(1024)
                    print(f"Received: {data.decode('utf-8')}")
    except ssl.SSLError as e:
        print(f"SSL Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def print_cert_details(cert):
    """
    Print certificate details (subject, issuer, expiration).
    """
    subject = dict(x[0] for x in cert['subject'])
    issuer = dict(x[0] for x in cert['issuer'])

    print("\nCertificate Subject Details (Issued To):")
    for key, value in subject.items():
        print(f"  {key}: {value}")

    print("\nCertificate Issuer Details (Issued By):")
    for key, value in issuer.items():
        print(f"  {key}: {value}")

    expiry_date = cert['notAfter']
    print(f"\nExpiry Date: {expiry_date}\n")

def main():
    # Get the provided command line options
    arguments = parse_cli()
    run_client(arguments.server, arguments.port, arguments.cert, arguments.key, arguments.cafile)

    # Run the Echo client
    # run_client("127.0.0.1", "fullchain_host2.crt", "host2.key", "rootCA.crt")

# Only run program when run directly from the command line, do nothing if imported
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as err:
        pass


# 7D
# python3 server.py fullchain_host1.crt host1.key rootCA.crt
# python3 client.py 127.0.0.1 fullchain_host2.crt host2.key rootCA.crt