"""The purpose of this class is communicating and resolving
utility parts of the Xavier API.

For example you can find here methods for creating account,
finding new users, cryptographic handshake operations and many more.

The design of this file is to be stateless and it does not contain
any objects which are changing the state of the elliot app
"""
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
from app.user_state import UserState


def update_one_time_key(
    url:str, user_state: UserState, new_key: X25519PublicKey, index: int
) -> None:
    ...


def get_random_one_time_key(
    url:str,
    user_state: UserState,
) -> Optional[X25519PublicKey]:
    ...


async def get_pending_responses(url:str, user_state:UserState) -> list[dict]:
    """
    Get list of all missed messages
    """
    ...


def register_user(url:str, user_state:UserState) -> bool:
    """Register new user to the server

    :param url: url path of the server
    :type url: str
    :param user_state: details about the user. 
        We take nessesary keys from here
    :type user_state: UserState
    :return: [description]
    :rtype: bool
    """
    ...

def authenticate_user(url:str, user_state:UserState, keys:dict) -> bool:
    """THIS WILL UPDATE USER_STATE AND ADD OAUTH TOKEN!!!"""
    ...

def send_contact_invite(url:str, user_state:UserState, contact:str, keys:dict) -> bool:
    """
    Send an invitation to the user that is the 
    owner of the given username
    Needed keys:
        - public id key ["id_key"]
        - public ephemeral key ["ephemeral_key"]

    Fails is contact has already used up his all
    otk keys

    :param url: url path of the server
    :type url: str
    :param user_state: [description]
    :type user_state: UserState
    :param contact: contact public username
    :type contact: str
    :param keys: dictionary of all nessesary keys to perform a transaction
    :type keys: dict
    :return: returns True if successful, otherwise False
    :rtype: bool
    """
    ...

