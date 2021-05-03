from app.user_state import UserState
from enum import Enum, auto
import json


class ResponseType(Enum):
    MESSAGE = auto()
    X3DH_SESSION_START = auto()
    X3DH_SESSION_HANDSHAKE = auto()
    AUTH = auto()


class ResponseParserException(Exception):
    ...


def parse_respose(raw: str) -> dict:
    out = json.loads(raw)
    return out


def build_response(
    user_state: UserState, type: ResponseType, keyes: dict
) -> str:
    ...
