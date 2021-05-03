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
    user_state: UserState, new_key: X25519PublicKey, index: int
) -> None:
    ...


def get_random_one_time_key(
    user_state: UserState,
) -> Optional[X25519PublicKey]:
    ...
