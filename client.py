import sys, time, msvcrt
import select
import socket
from threading import Lock
from utils import MAX_MESSAGE_SIZE

SOCKET_TIMEOUT = 1
INPUT_TIMEOUT = 5

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
                print('')
                break
            elif ord(byte_arr) >= 32:
                input += "".join(map(chr,byte_arr))
        if len(input) == 0 and (time.time() - start_time) > timeout:
            break
    return input

    
class Client:
   def __init__(self):
       self.client_socket = socket.socket()
       self.output_lock = Lock()
   
   """
   Recieves messages from server
   """
   @staticmethod
   def recieve_messages(self):
        try:
            while True:
                read_list, _, _ = select.select([self.client_socket], [], [], SOCKET_TIMEOUT)
                if self.client_socket in read_list:
                    self.output_lock.acquire()
                    message = self.client_socket.recv(MAX_MESSAGE_SIZE).decode()
                    message = message.split('\n')
                    message.remove(message[-1])
                    for single_message in message:
                        print(single_message)
                    self.output_lock.release()
        except Exception as e:
            self.output_lock.release()
            return
    