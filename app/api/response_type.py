from enum import Enum


class ResponseType(Enum):
    TEXT_MESSAGE = 1
    X3DH_SESSION_START = 2
    X3DH_SESSION_HANDSHAKE = 3
    AUTH = 4
