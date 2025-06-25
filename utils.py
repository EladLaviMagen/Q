from enum import Enum


ADDRESS = "127.0.0.1"
MAX_USERS = 10
MAX_MESSAGE_SIZE = 1024
NAME = 0
ROOM = 1
EXIT = "exit"
TRANSFER = "transfer"
NOTIFY_ROOM_MESSAGE_ENTRY = "has entered the room"
NOTIFY_ROOM_MESSAGE_LEAVING = "transferred to a different room"
NOTIFY_LEAVE_MESSAGE = "left"
TIMEOUT = 10
TRANSFER_ERROR_MESSAGES = ["TRANSFER REQUEST WAS NOT PROPER - Usage : /transfer <room name>\n",
                           "ADMIN CANNOT TRANSFER\n",
                           "UNAUTHORIZED ENTRY ATTEMPT TO ADMIN ROOM, ONLY ADMINS IN ADMIN ROOM\n"]
KICK_ERROR_MESSAGES = ["KICK REQUEST WAS NOT PROPER\nUsage : /kick <user name>\n",
                        """YOU ARE ATTEMPTING TO KICK YOURSELF, PLEASE USE "/exit" INSTEAD\n""",
                        "THE USER YOU ARE ATTEMPTING TO KICK IS NOT IN THIS ROOM\n"]
UNKNOWN_COMMAND_ERROR = "UNKNOWN COMMAND ATTEMPTED\n"
ADMIN = "ADMIN"
COMMAND = '/'
COMMAND_IDENTIFIER = 0
KICKED_USER = 1

class CommonReturnCodes(Enum):
    VALID = -1
    BAD_USAGE_CODE = 0

class TransferReturnCodes(Enum):
    ADMIN_TRANSFER_CODE = 1
    UNAUTHORIZED_ENTRY_CODE = 2
    
 
 class KickReturnCodes(Enum):
    KICK_SELF_CODE = 1
    USER_NOT_FOUND_CODE = 2