from app import create_app

import argparse
import os
import socket

"""
This is the entry point for the server.
"""

if __name__ == '__main__':
    print('Starting the server...')

    # parse port number from command line arguments using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='port number')
    args = parser.parse_args()
    port = args.port

    # check if the port number is valid
    if port < 1024 or port > 65535:
        print('Port number should be in the range of 1024 to 65535')
        exit()

    # check if the port number is already in use
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     if s.connect_ex(('127.0.0.1', port)) == 0:
    #         print('Port number is already in use')
    #         exit()

    app = create_app()

    # disable reload, otherwise the port gets reset to default
    app.run(debug=True, use_reloader=False, port=port)