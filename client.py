import sys, time, msvcrt
import select
import socket
from utils import MAX_MESSAGE_SIZE

SOCKET_TIMEOUT = 2
INPUT_TIMEOUT = 5
    
    
class Client:
   client_socket = socket.socket()
   @staticmethod
   def recieve_messages():
        try:
            while True:
                read_list, _, _ = select.select([Client.client_socket], [], [], SOCKET_TIMEOUT)
                if Client.client_socket in read_list:
                    message = Client.client_socket.recv(MAX_MESSAGE_SIZE).decode()
                    message = message.split('\n')
                    message.remove(message[-1])
                    for single_message in message:
                        print(single_message)
        except Exception as e:
            return
    