"""
TCP Echo Server Program

Opens up a listening TCP socket on the nominated port. For all connected clients, will wait for an incoming message
and then echo back to the client

  usage: server.py [-h] [-p PORT]

  TCP Echo Server

  options:
    -h, --help            show this help message and exit
    -p PORT, --port PORT  Port number to run the TLS echo server on (default=1024)

Written by Jason But
Copyright 2024
"""
import os

import socket

import argparse

import threading

import ssl # ADD!

from datetime import datetime # ADD!

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
    parser = argparse.ArgumentParser(description='TCP Echo Server', formatter_class=argparse.RawTextHelpFormatter,
                                     allow_abbrev=False)

    # Uncomment the line below to add options for Lab 6 allowing specification of Server certificate and key
    parser.add_argument('cert', type=ValidFile(), help='Location of Server Public Certificate File')
    parser.add_argument('key', type=ValidFile(), help='Location of Server Private Key')

    parser.add_argument('cafile', type=ValidFile(), help='Location of Root CA File')

    parser.add_argument('-p', '--port', type=IntRange(1024, 16384), default=1024,
                        help='Port number to run the TLS echo server on (default=1024)')
    
    # Uncomment the line below to add options for Lab 7 allowing specification of certificate to use to validate client
    parser.add_argument('-v', '--validate_client', type=ValidFile(), help='Location of Certificate File to validate client. If provided, client certificate must either match this certificate or be signed by this certificate')

    return parser.parse_args()


def handle_client(sslsock):
    """
    Loop until a connected client disconnects. Echo all received data back to the client
    :param client: TCP Socket handling connection to remote side
    :param client_id: String with description of connected client for display
    """
    try:
        cert = sslsock.getpeercert()
        print_cert_details(cert)

        # Receive and echo back data
        while True:
            data = sslsock.recv(1024)  # Receive data from client
            if not data:
                break  # Client disconnected
            print(f"Received data: {data.decode('utf-8')}")
            sslsock.sendall(data)  # Echo back the received data

    except ssl.SSLError as e:
        print(f"SSL Error: {e}")
    finally:
        sslsock.close()  # Close the connection when done


def run_server(certfile, keyfile, cafile, port):
    """
    Run the TLS server with mutual authentication.
    :param certfile: Server certificate file (full chain)
    :param keyfile: Server private key file
    :param cafile: Root CA file for client authentication
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # Load the server's full certificate chain
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    
    # Require client certificate verification
    context.load_verify_locations(cafile=cafile)
    context.verify_mode = ssl.CERT_REQUIRED
    
    bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsocket.bind(('0.0.0.0', port))  # Bind to all available interfaces and port 1024
    bindsocket.listen(5)  # Listen for up to 5 connections
    
    print("Waiting for connection...")

    while True:
        newsocket, fromaddr = bindsocket.accept()  # Accept new connection
        try:
            sslsock = context.wrap_socket(newsocket, server_side=True)  # Wrap the socket with SSL
            print(f"Connection from {fromaddr}")

            handle_client(sslsock)  # Handle client communication

        except ssl.SSLError as e:
            print(f"SSL Error: {e}")
        finally:
            newsocket.close()  # Close the raw socket


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

# Function execute the actual program
def main():
    """
    Main program
    """
    # Get the provided command line options
    arguments = parse_cli() 
    run_server(arguments.cert, arguments.key, arguments.cafile, arguments.port)

    # Run the Echo Server
    # run_server("fullchain_host1.crt", "host1.key", "rootCA.crt")

# Only run program when run directly from the command line, do nothing if imported
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as err:
        pass