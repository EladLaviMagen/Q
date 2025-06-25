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


def main():
    args = get_args()
    client = Client()
    client.client_socket.connect((args.ip, args.port))
    client.client_socket.send((args.name + '-' + args.room_name).encode())
    client_input = ""
    reciever_thread = Thread(target=client.recieve_messages, args=(client,))
    reciever_thread.start()
    while not client_input.startswith(COMMAND + EXIT):
        client_input = ""
        client.output_lock.acquire()
        client_input = readInput(INPUT_TIMEOUT)
        client.output_lock.release()
        if client_input != "":
            client.client_socket.send(client_input.encode())
    client.client_socket.close()


if __name__ == "__main__":
    main()
