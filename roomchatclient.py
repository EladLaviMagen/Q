import argparse
import select
from threading import Thread
from utils import EXIT, COMMAND
from client import *


"""
Gets arguments from command line using argParse
@Return - The arguments
"""
def get_args():
    parser = argparse.ArgumentParser(description='Starts client')
    parser.add_argument('ip', type=str, help='Server ip')
    parser.add_argument('port', type=int, help='Server ip')
    parser.add_argument('name', type=str, help='Username')
    parser.add_argument('room_name', type=str, help='Room to enter', nargs='?', default="ADMIN")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    Client.client_socket.connect((args.ip, args.port))
    Client.client_socket.send((args.name + '-' + args.room_name).encode())
    client_input = ""
    reciever_thread = Thread(target=Client.recieve_messages)
    reciever_thread.start()
    while not client_input.startswith(COMMAND + EXIT):
        client_input = ""
        client_input = input()
        if client_input != "":
            Client.client_socket.send(client_input.encode())
    Client.client_socket.close()
