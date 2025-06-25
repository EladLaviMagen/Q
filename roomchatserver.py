import socket
import select
import argparse
from collections import defaultdict


ADDRESS = "127.0.0.1"
MAX_USERS = 10
MAX_MESSAGE_SIZE = 1024
NAME = 0
ROOM = 1
EXIT = "/exit"
TRANSFER = "/transfer"
NOTIFY_ROOM_MESSAGE_ENTRY = "has entered the room"
NOTIFY_ROOM_MESSAGE_LEAVING = "transferred to a different room"
NOTIFY_LEAVE_MESSAGE = "left"
TIMEOUT = 10
VALID = -1
BAD_USAGE_CODE = 0
ADMIN_TRANSFER_CODE = 1
UNAUTHORIZED_ENTRY_CODE = 2
TRANSFER_ERROR_MESSAGES = ["ERROR : TRANSFER REQUEST WAS NOT PROPER - Usage : /transfer <room name>\n",
                           "ERROR : ADMIN CANNOT TRANSFER\n",
                           "ERROR : UNAUTHORIZED ENTRY ATTEMPT TO ADMIN ROOM, ONLY ADMINS IN ADMIN ROOM\n"]
UNKNOWN_COMMAND_ERROR = "ERROR : UNKNOWN COMMAND ATTEMPTED\n"
ADMIN = "ADMIN"
COMMAND = '/'
COMMAND_NAME = 0

"""
Gets server port from arguments
"""
def get_port():
    parser = argparse.ArgumentParser(description='Starts server')
    parser.add_argument('port', metavar='N', type=int, help='Server port')
    return parser.parse_args().port


"""
Handles new user entering the room-chat server
@Param server_socket - The server socket
"""
def handle_new_user(server_socket):
    new_socket, _ = server_socket.accept()
    wait_list.append(new_socket)
    entry_message = new_socket.recv(MAX_MESSAGE_SIZE).decode()
    entry_message = entry_message.split('-')
    rooms[entry_message[ROOM]].append(new_socket)
    sockets_info[new_socket] = [entry_message[NAME], entry_message[ROOM]]
    print(entry_message[NAME], "has entered room", entry_message[ROOM])
    handle_message(new_socket, NOTIFY_ROOM_MESSAGE_ENTRY)


"""
Handles user messages
@Param sender_socket - The socket that message was sent from
@param client_message - The message sent by the client
@Param delim - Delimeter for message, defaults to space - ' '
"""
def handle_message(sender_socket, client_message, delim=" "):
    # In the cases of commands, special message are sent for the other users
    client_message = sockets_info[sender_socket][NAME] + delim + client_message + '\n'
    # Sending message to all the required users
    send_list = rooms[sockets_info[sender_socket][ROOM]] + rooms[ADMIN]
    if sockets_info[sender_socket][ROOM] == ADMIN:
        send_list = sockets_info.keys()
    for client in send_list:
        if client != sender_socket:
            client.send(client_message.encode())



"""
Handles user leaving
@Param leaving_socket - The socket of the user that is leaving
@Param exit_request - details for the exit request, as of now unused, but I thought of implementing a goodbye message feature to /exit
"""
def handle_exit(leaving_socket, exit_request):
    # Updating room and deleting client information
    handle_message(leaving_socket, NOTIFY_LEAVE_MESSAGE)
    rooms[sockets_info[leaving_socket][ROOM]].remove(leaving_socket)
    sockets_info.pop(leaving_socket)
    wait_list.remove(leaving_socket)
    leaving_socket.close()


"""
Validates transfer request
@Param transferred_socket - The socket of the user that is transferring rooms
@param transfer_request - Parameters of request
@Return - Result code for transfer request
"""
def validate_transfer(sender_socket, transfer_request):
    if sockets_info[sender_socket][ROOM] == ADMIN:
        return ADMIN_TRANSFER_CODE
    if len(transfer_request) != 2:
        return BAD_USAGE_CODE
    if transfer_request[ROOM] == ADMIN:
        return UNAUTHORIZED_ENTRY_CODE
    return VALID


"""
Handles user room transfer
@Param transferred_socket - The socket of the user that is transferring rooms
@param transfer_request - Parameters of request
"""
def handle_transfer(transferred_socket, transfer_request):
    # Updating rooms and client information
    result = validate_transfer(transferred_socket, transfer_request)
    if result == VALID:
        handle_message(transferred_socket, NOTIFY_ROOM_MESSAGE_LEAVING)
        rooms[sockets_info[transferred_socket][ROOM]].remove(transferred_socket)
        sockets_info[transferred_socket][ROOM] = transfer_request[ROOM]
        rooms[transfer_request[ROOM]].append(transferred_socket)
        # Sending a message to the new room that client has joined
        handle_message(transferred_socket, NOTIFY_ROOM_MESSAGE_ENTRY)
    else:
        transferred_socket.send(TRANSFER_ERROR_MESSAGES[result].encode())




COMMAND_HANDLER = {EXIT : handle_exit, TRANSFER : handle_transfer}
rooms = defaultdict(list)
sockets_info = {}
wait_list = []

if __name__ == "__main__":
    server = socket.socket()
    server.bind((ADDRESS, get_port()))
    server.listen(MAX_USERS)
    wait_list = [server]
    while True:
        to_read, _, _, = select.select(wait_list, [], [], TIMEOUT)
        for sock in to_read:
            if sock == server:
                handle_new_user(server)
            else:
                msg = sock.recv(MAX_MESSAGE_SIZE).decode()
                if msg[0] == COMMAND:
                    command_params = msg.split(' ')
                    if command_params[0] in COMMAND_HANDLER.keys():
                        COMMAND_HANDLER[command_params[COMMAND_NAME]](sock, command_params)
                    else:
                        sock.send(UNKNOWN_COMMAND_ERROR.encode())
                else:
                    handle_message(sock, msg, " : ")

