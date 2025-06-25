import socket
import select
import argparse
from collections import defaultdict
from server import *

COMMAND_HANDLER = {EXIT : Server.handle_exit, TRANSFER : Server.handle_transfer}

"""
Gets server port from arguments
"""
def get_port():
    parser = argparse.ArgumentParser(description='Starts server')
    parser.add_argument('port', metavar='N', type=int, help='Server port')
    return parser.parse_args().port


def main():
    server_connection = socket.socket()
    server_connection.bind((ADDRESS, get_port()))
    server_connection.listen(MAX_USERS)
    Server.wait_list = [server_connection]
    while True:
        to_read, _, _, = select.select(Server.wait_list, [], [], TIMEOUT)
        for sock in to_read:
            if sock == server_connection:
                Server.handle_new_user(server_connection)
            else:
                msg = sock.recv(MAX_MESSAGE_SIZE).decode()
                if msg.startswith(COMMAND):
                    msg = msg[1:]
                    command_params = msg.split(' ')
                    if command_params[COMMAND_IDENTIFIER] in COMMAND_HANDLER.keys():
                        COMMAND_HANDLER[command_params[COMMAND_IDENTIFIER]](sock, command_params)
                    else:
                        sock.send(UNKNOWN_COMMAND_ERROR.encode())
                else:
                    Server.handle_message(sock, msg, " : ")


if __name__ == "__main__":
    main()


