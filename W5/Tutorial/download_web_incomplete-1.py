
# !/usr/bin/env python3.7

"""
Sample HTTP download program
"""

# Application libraries
import argparse
import os
import socket
import ssl

class ValidFile:
    def __call__(self, arg) -> str:
        if not os.path.exists(arg):
            raise argparse.ArgumentTypeError(f'Nominated file "{arg}" does not exist')
        return arg

def parse_cli():
    parser = argparse.ArgumentParser(description='Download Web Page', formatter_class=argparse.RawTextHelpFormatter, allow_abbrev=False)
    parser.add_argument('server', help='Name of server to connect to')
    return parser.parse_args()

def run_client(arguments): # TODO
    # Step 1: Create a socket, wrap it with TLS Context and Verifying Connection
    context = ssl.create_default_context()
    with socket.create_connection((arguments.server, 443)) as sock: # port 443 host https access
        with context.wrap_socket(sock, server_hostname=arguments.server) as secure_sock:
            print(f"Connected to {arguments.server}")
            # Step 2: Downloading a page
            request = f"GET / HTTP/1.1\r\nHost: {arguments.server}\r\nConnection: close\r\n\r\n" # Send a GET request for download the page
            secure_sock.send(request.encode())
            # Step 3: Connect and Download page from Rule201
            response = b""
            while True:
                chunk = secure_sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            print(response.decode())

def main():
    # Get the user provided parameters
    arguments = parse_cli()
    # Fetch and print the downloaded page to the screen
    run_client(arguments)

# Only run program when run directly from the command line, do nothing if imported
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

    