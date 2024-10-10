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
 
    parser.add_argument('-p', '--port', type=IntRange(1024, 16384), default=1024, help='Port number to run the TLS echo server on (default=1024)')

    parser.add_argument('server', help='Name of server to connect to')

    # Uncomment the line below to add options for Lab 6 allowing specification of server certificate, and optionally server commonname
    parser.add_argument('cert', type=ValidFile(), help='Location of Server Public Certificate File to use to validate server')
    parser.add_argument('-c', '--common_name', help="Common Name of server certificate if it is different than server as listed above")

    # Uncomment the line below to add options for Lab 7 allowing specification of Client certificate and key to use to validate client to server
    parser.add_argument('-v', '--validate_client', nargs=2, type=ValidFile(), help='Location of Certificate File to use to validate client to server. First file is the Public Client Certificate, the second is the Private Client Key')

    return parser.parse_args()

def run_client(arguments):
    """
    Run the TLS Echo Client

    :param arguments: Parsed arguments to use to run server
        arguments.port:             Port number to run server on
        arguments.server:           Name (or IP address) of server to connect to (needed for lab 6)
        arguments.cert:             Certificate file to validate server (needed for lab 6)
        arguments.common_name:      Common name to use to validate server - if not specified set to arguments.server (needed for lab 6)
        arguments.validate_client:  [ certificate file, private key file ] for client (needed for lab 7)
    """
    # Create an SSL context for secure communication
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=arguments.cert)

    # Check hostname only if a common name is provided
    if arguments.common_name:
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
    else:
        context.check_hostname = False

    # Validate client
    if arguments.validate_client:
        context.load_cert_chain(certfile=arguments.validate_client[0], keyfile=arguments.validate_client[1])

    # Create a standard TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Wrap the TCP socket with SSL/TLS
        ssl_sock = context.wrap_socket(sock, server_hostname=arguments.common_name if arguments.common_name else arguments.server)
        # Connect to the server using the wrapped socket
        ssl_sock.connect((arguments.server, arguments.port))
        print(f'TLS Connection established. {ssl_sock.getpeername()}')

        # ADD FOR 6C!
        cert = ssl_sock.getpeercert()
        print_cert_details(cert)
        # END!

        while True:
            msg = input('Message to send (empty line terminates):')

            if not msg:
                break

            print(f'Sending: {msg}')
            # Use the SSL wrapped socket for sending
            ssl_sock.send(msg.encode('utf-8'))
            data = ssl_sock.recv(1024)
            print(f'Received reply: {data.decode("utf-8")}')
        print("Closing connection")
        ssl_sock.close()

    except ssl.SSLError as e: # Handle exception
        print(f"SSL Error: {e}. Certificate mismatch or verification failed.")
        sock.close()

# Additional function for 6C!
# Printing certs details and locations, from both the issuer and issued, with expiry date
def print_cert_details(cert):
    """
    Print detailed information from the server certificate.
    """
    # Subject details (Issued to)
    subject = dict(x[0] for x in cert['subject'])
    print("\nCertificate Subject Details (Issued To):")
    for key, value in subject.items():
        print(f"  {key}: {value}")

    # Issuer details (Signed by)
    issuer = dict(x[0] for x in cert['issuer'])
    print("\nCertificate Issuer Details (Issued By):")
    for key, value in issuer.items():
        print(f"  {key}: {value}")

    # Expiry date
    expiry_date_str = cert['notAfter']
    expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
    print(f"\nExpiry Date: {expiry_date}\n")

def main():
    # Get the provided command line options
    arguments = parse_cli()

    # Run the Echo client
    run_client(arguments)


# Only run program when run directly from the command line, do nothing if imported
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as err:
        pass


# BASH SHORTCUT
# SHARED SELF-SIGNED CERT
# python3 server.py -p 1024 shared_cert.pem shared_key.pem -v shared_cert.pem
# python3 client.py -p 1024 localhost shared_cert.pem -v shared_cert.pem shared_key.pem
# DIFFERENT SELF-SIGNED CERT
# python3 server.py -p 1024 server_cert.pem server_key.pem -v client_cert.pem
# python3 client.py -p 1024 localhost server_cert.pem -v client_cert.pem client_key.pem