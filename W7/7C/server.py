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

    parser.add_argument('-p', '--port', type=IntRange(1024, 16384), default=1024,
                        help='Port number to run the TLS echo server on (default=1024)')

    # Uncomment the line below to add options for Lab 6 allowing specification of Server certificate and key
    parser.add_argument('cert', type=ValidFile(), help='Location of Server Public Certificate File')
    parser.add_argument('key', type=ValidFile(), help='Location of Server Private Key')

    # Uncomment the line below to add options for Lab 7 allowing specification of certificate to use to validate client
    parser.add_argument('-v', '--validate_client', type=ValidFile(), help='Location of Certificate File to validate client. If provided, client certificate must either match this certificate or be signed by this certificate')

    return parser.parse_args()


def handle_client(client: socket.socket, client_id: str):
    """
    Loop until a connected client disconnects. Echo all received data back to the client
    :param client: TCP Socket handling connection to remote side
    :param client_id: String with description of connected client for display
    """
    try:
        print(f'Client connected: {client_id}')
        cert = client.getpeercert()
        print_cert_details(cert)

        while True:
            # Get next block of data from remote client
            data = client.recv(1024)

            # If data is invalid, the remote end has closed the connection, break loop to return
            if not data: break

            # Return sent data to client
            print(f'Thread({client_id}): Echoing data ({data.decode("utf-8")})')
            client.send(data)

    finally:
        # Close socket connection
        client.close()
        print(f'Thread({client_id}): Connection Closed')


def run_server(arguments):
    """
    Create a TCP server using the information provided in arguments and return the socket

    :param arguments: Parsed arguments to use to run server
        arguments.port:             Port number to run server on
        arguments.cert:             Certificate file for server (needed for lab 6)
        arguments.key:              Private key file for server (needed for lab 6)
        arguments.validate_client:  Certificate file to validate client (needed for lab 7)
    """
    # ADD! Wrap the Server Socket with SSL/TLS:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=arguments.cert, keyfile=arguments.key)

    # Validate client
    if arguments.validate_client:
        # Enable client authentication
        context.load_verify_locations(cafile=arguments.validate_client)
        context.verify_mode = ssl.CERT_REQUIRED

    # Create listening socket
    bindsocket = socket.socket()
    bindsocket.bind(('0.0.0.0', arguments.port))
    bindsocket.listen(5)

    while True:
        print('Parent: Waiting for connection')
        # Accept new connection from remote system
        newsocket, fromaddr = bindsocket.accept()
        try: 
            # Wrap socket with SSL
            sslsocket = context.wrap_socket(newsocket, server_side=True)
            print(f'Connection established with {fromaddr}')
            # Create and start the thread to handle the client. Thread will self-terminate when when client closes the connection
            # thread = threading.Thread(target=handle_client, args=(newsocket, f'{fromaddr[0], fromaddr[1]}'))
            thread = threading.Thread(target=handle_client, args=(sslsocket, f'{fromaddr[0], fromaddr[1]}'))
            thread.start()
        except ssl.SSLError as e: # Handle exception
            print(f"SSL Error: {e}. Certificate mismatch or verification failed.")
            newsocket.close()

def print_cert_details(cert):
    """
    Print detailed information from the client/server certificate.
    """
    subject = dict(x[0] for x in cert['subject'])
    issuer = dict(x[0] for x in cert['issuer'])
    
    # Print details
    print("\nCertificate Subject Details (Issued To):")
    for key, value in subject.items():
        print(f"  {key}: {value}")
        
    print("\nCertificate Issuer Details (Issued By):")
    for key, value in issuer.items():
        print(f"  {key}: {value}")

    expiry_date_str = cert['notAfter']
    expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
    print(f"\nExpiry Date: {expiry_date}\n")

# Function execute the actual program
def main():
    """
    Main program
    """
    # Get the provided command line options
    arguments = parse_cli()

    # Run the Echo Server
    run_server(arguments)


# Only run program when run directly from the command line, do nothing if imported
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as err:
        pass