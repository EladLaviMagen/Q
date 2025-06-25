import socket
import argparse
import select
import sys, time, msvcrt

MAX_MESSAGE_SIZE = 1024
EXIT = "/exit"
SOCKET_TIMEOUT = 2
INPUT_TIMEOUT = 5

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

"""
A function that reads input with a timeout
"""
def readInput(timeout):
    start_time = time.time()
    input = ''
    while True:
        if msvcrt.kbhit():
            byte_arr = msvcrt.getche()
            if ord(byte_arr) == 13:
                break
            elif ord(byte_arr) >= 32:
                input += "".join(map(chr,byte_arr))
        if len(input) == 0 and (time.time() - start_time) > timeout:
            break
    print('')
    return input


if __name__ == "__main__":
    client = socket.socket()
    args = get_args()
    client.connect((args.ip, args.port))
    client.send((args.name + '-' + args.room_name).encode())
    client_input = ""
    client.setblocking(False)
    while client_input != EXIT:
        client_input = ""
        read_list, _, _ = select.select([client], [], [], SOCKET_TIMEOUT)
        if client in read_list:
            message = client.recv(MAX_MESSAGE_SIZE).decode()
            message = message.split('\n')
            message.remove(message[-1])
            for single_message in message:
                print(single_message)
        client_input = readInput(INPUT_TIMEOUT)
        if client_input != "":
            client.send(client_input.encode())
    client.close()
