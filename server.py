import socket
from collections import defaultdict
from utils import *


class Server:
    wait_list = []
    _rooms = defaultdict(list)
    _sockets_info = {}


    """
    Handles new user entering the room-chat server
    @Param server_socket - The server socket
    """
    @staticmethod
    def handle_new_user(server_socket):
        new_socket, _ = server_socket.accept()
        Server.wait_list.append(new_socket)
        entry_message = new_socket.recv(MAX_MESSAGE_SIZE).decode()
        entry_message = entry_message.split('-')
        Server._rooms[entry_message[ROOM]].append(new_socket)
        Server._sockets_info[new_socket] = [entry_message[NAME], entry_message[ROOM]]
        print(entry_message[NAME], "has entered room", entry_message[ROOM])
        Server.handle_message(new_socket, NOTIFY_ROOM_MESSAGE_ENTRY)

    """
    Handles user messages
    @Param sender_socket - The socket that message was sent from
    @param client_message - The message sent by the client
    @Param delim - Delimeter for message, defaults to space - ' '
    """
    @staticmethod
    def handle_message(sender_socket, client_message, delim=" "):
        # In the cases of commands, special message are sent for the other users
        client_message = Server._sockets_info[sender_socket][NAME] + delim + client_message + '\n'
        # Sending message to all the required users
        send_list = Server._rooms[Server._sockets_info[sender_socket][ROOM]] + Server._rooms[ADMIN]
        if Server._sockets_info[sender_socket][ROOM] == ADMIN:
            send_list = Server._sockets_info.keys()
        for client in send_list:
            if client != sender_socket:
                client.send(client_message.encode())

    """
    Handles user leaving
    @Param leaving_socket - The socket of the user that is leaving
    @Param exit_request - details for the exit request, as of now unused, but I thought of implementing a goodbye message feature to /exit
    """
    @staticmethod
    def handle_exit(leaving_socket, exit_request):
        # Updating room and deleting client information
        Server.handle_message(leaving_socket, NOTIFY_LEAVE_MESSAGE)
        Server._rooms[Server._sockets_info[leaving_socket][ROOM]].remove(leaving_socket)
        Server._sockets_info.pop(leaving_socket)
        Server.wait_list.remove(leaving_socket)
        leaving_socket.close()

    """
    Validates transfer request
    @Param transferred_socket - The socket of the user that is transferring Server._rooms
    @param transfer_request - Parameters of request
    @Return - Result code for transfer request
    """
    @staticmethod
    def _validate_transfer(sender_socket, transfer_request):
        if Server._sockets_info[sender_socket][ROOM] == ADMIN:
            return TransferReturnCodes.ADMIN_TRANSFER_CODE
        if len(transfer_request) != 2:
            return TransferReturnCodes.BAD_USAGE_CODE
        if transfer_request[ROOM] == ADMIN:
            return TransferReturnCodes.UNAUTHORIZED_ENTRY_CODE
        return TransferReturnCodes.VALID

    """
    Handles user room transfer
    @Param transferred_socket - The socket of the user that is transferring Server._rooms
    @param transfer_request - Parameters of request
    """
    @staticmethod
    def handle_transfer(transferred_socket, transfer_request):
        # Updating Server._rooms and client information
        result = Server._validate_transfer(transferred_socket, transfer_request)
        if result == TransferReturnCodes.VALID:
            Server.handle_message(transferred_socket, NOTIFY_ROOM_MESSAGE_LEAVING)
            Server._rooms[Server._sockets_info[transferred_socket][ROOM]].remove(transferred_socket)
            Server._sockets_info[transferred_socket][ROOM] = transfer_request[ROOM]
            Server._rooms[transfer_request[ROOM]].append(transferred_socket)
            # Sending a message to the new room that client has joined
            Server.handle_message(transferred_socket, NOTIFY_ROOM_MESSAGE_ENTRY)
        else:
            transferred_socket.send(TRANSFER_ERROR_MESSAGES[result.value].encode())

    """
    Validates transfer request
    @Param transferred_socket - The socket of the user that is transferring Server._rooms
    @param transfer_request - Parameters of request
    @Return - Result code for transfer request
    """
    @staticmethod
    def _validate_kick(sender_socket, kick_request):
        if len(kick_request) != 2:
            return CommonReturnCodes.BAD_USAGE
        kicked_user = kick_request[KICKED_USER]
        if kicked_user == Server.sockets_info[sender_socket]:
            return KickReturnCodes.KICK_SELF_CODE
        for client_socket in Server._rooms[Server._sockets_info[sender_socket][ROOM]]:
            if Server._sockets_info[client_socket][NAME] == kicked_user:
                return CommonReturnCodes.VALID
        return KickReturnCodes.USER_NOT_FOUND_CODE

    """
    Handles user room transfer
    @Param transferred_socket - The socket of the user that is transferring Server._rooms
    @param transfer_request - Parameters of request
    """
    @staticmethod
    def handle_kick(transferred_socket, kick_request):
        # Updating Server._rooms and client information
        result = Server._validate_kick(transferred_socket, kick_request)
        if result == CommonReturnCodes.VALID:
            Server.handle_message(transferred_socket, NOTIFY_ROOM_MESSAGE_LEAVING)
            Server._rooms[Server._sockets_info[transferred_socket][ROOM]].remove(transferred_socket)
            Server._sockets_info[transferred_socket][ROOM] = transfer_request[ROOM]
            Server._rooms[transfer_request[ROOM]].append(transferred_socket)
            # Sending a message to the new room that client has joined
            Server.handle_message(transferred_socket, NOTIFY_ROOM_MESSAGE_ENTRY)
        else:
            transferred_socket.send(TRANSFER_ERROR_MESSAGES[result.value].encode())
