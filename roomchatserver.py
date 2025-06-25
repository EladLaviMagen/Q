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
KICK = "/kick"
KICKED_USER = 1
TRANSFER = "/transfer"
NOTIFY_ROOM_MESSAGE = "has entered the room"
TIMEOUT = 10
TRANSFER_ERROR_BAD_USAGE = "ERROR : TRANSFER REQUEST WAS NOT PROPER\nUsage : /transfer <room name>\n"
TRANSFER_ERROR_ADMIN = "ERROR : ADMIN CANNOT TRANSFER\n"
TRANSFER_ERROR_UNAUTHORIZED = "Unauthorized entry attempt, only admins in the ADMIN room\n"
KICK_ERROR_BAD_USAGE = "ERROR : KICK REQUEST WAS NOT PROPER\nUsage : /kick <user name>\n"
KICK_ERROR_KICK_SELF = """ERROR : YOU ARE ATTEMPTING TO KICK YOURSELF, PLEASE USE "/exit" INSTEAD\n"""
KICK_ERROR_USER_NOT_FOUND = "ERROR : THE USER YOU ARE ATTEMPTING TO KICK IS NOT IN THIS ROOM\n"
ADMIN = "ADMIN"


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
    handle_message(new_socket, NOTIFY_ROOM_MESSAGE)


"""
Handles user messages
@Param sender_socket - The socket that message was sent from
@param client_message - The message sent by the client
"""
def handle_message(sender_socket, client_message):
    # In the cases of commands, special message are sent for the other users
    if client_message == EXIT:
        client_message = sockets_info[sender_socket][NAME] + " left" + '\n'
    elif client_message.startswith(TRANSFER):
        client_message = sockets_info[sender_socket][NAME] + " transferred to a different room" + '\n'
    else:
        client_message = sockets_info[sender_socket][NAME] + " : " + client_message + '\n'
    # Sending message to all the required users
    send_list = rooms[sockets_info[sender_socket][ROOM]] + rooms[ADMIN]
    if sockets_info[sender_socket][ROOM] == ADMIN:
        send_list = sockets_info.keys()
    for client in send_list:
        if client != sender_socket:
            client.send(client_message.encode())


"""
Handles user room transfer
@Param transferred_socket - The socket of the user that is transferring rooms
@param new_room - The new room name to move to
"""
def handle_transfer(transferred_socket, new_room):
    # Updating rooms and client information
    rooms[sockets_info[transferred_socket][ROOM]].remove(transferred_socket)
    sockets_info[transferred_socket][ROOM] = new_room
    rooms[new_room].append(transferred_socket)
    # Sending a message to the new room that client has joined
    handle_message(transferred_socket, NOTIFY_ROOM_MESSAGE)


"""
Handles user leaving
@Param leaving_socket - The socket of the user that is leaving
"""
def handle_exit(leaving_socket):
    # Updating room and deleting client information
    rooms[sockets_info[leaving_socket][ROOM]].remove(leaving_socket)
    sockets_info.pop(leaving_socket)
    wait_list.remove(leaving_socket)
    leaving_socket.close()


"""
Checks if what the user is attempting to perform/send is valid
Also sends back error message to user if he sent invalid message
@Param sender_socket - the socket of the sender
@param sent_message - the message he is attempting to send to others
@return True if the message/action is valid and should be handled, false otherwise
"""
def is_valid(sender_socket, sent_message):
    if sent_message.startswith(TRANSFER):
        return validate_transfer(sender_socket, sent_message)
    if sent_message.startswith(KICK):
        return validate_kick(sender_socket, sent_message)
    return True


def validate_transfer(sender_socket, transfer_request):
    if sockets_info[sender_socket][ROOM] == ADMIN:
        sender_socket.send(TRANSFER_ERROR_ADMIN.encode())
        return False
    transfer_request = transfer_request.split(' ')
    if len(transfer_request) != 2:
        sender_socket.send(TRANSFER_ERROR_BAD_USAGE.encode())
        return False
    if transfer_request[ROOM] == ADMIN:
        sender_socket.send(TRANSFER_ERROR_UNAUTHORIZED.encode())
        return False
    return True


def validate_kick(sender_socket, kick_request):
    kick_request = kick_request.split(' ')
    if len(kick_request) != 2:
        sender_socket.send(KICK_ERROR_BAD_USAGE.encode())
        return False
    kicked_user = kick_request[KICKED_USER]
    if kicked_user == sockets_info[sender_socket]:
        sender_socket.send(KICK_ERROR_BAD_USAGE.encode())
        return False
    for client_socket in rooms[sockets_info[sender_socket][ROOM]]:
        if sockets_info[client_socket][NAME] == kicked_user:
            return True
    sender_socket.send(KICK_ERROR_USER_NOT_FOUND.encode())
    return False


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
                if not is_valid(sock, msg):
                    continue
                handle_message(sock, msg)
                if msg == EXIT:
                    handle_exit(sock)
                elif msg.startswith(TRANSFER):
                    handle_transfer(sock, msg.split(' ')[ROOM])
