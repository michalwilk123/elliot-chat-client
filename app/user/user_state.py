from app.chat.crypto.crypto_utils import create_b64_from_private_key
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from typing import Optional
import binascii


class UserStateException(Exception):
    ...


class UserState:
    """
    Current informations about the app state.
    This functionality is based on redux state class.
    Using slots because atributes in this class will be accessed
    quite frequently. Data in this class is not declared on the
    startup.
    """

    __slots__ = ("_login", "_password", "_id_key", "_signed_pre_key")

    def __init__(self, login: str):
        self._login: str = login
        self._id_key: Optional[X25519PrivateKey] = None
        self._signed_pre_key: Optional[X25519PrivateKey] = None

    @property
    def login(self) -> str:
        return self._login

    @property
    def id_key(self) -> Optional[X25519PrivateKey]:
        return self._id_key

    @property
    def signed_pre_key(self) -> Optional[X25519PrivateKey]:
        return self._signed_pre_key

    @property
    def signature(self) -> bytes:
        if self.id_key is None or self.signed_pre_key is None:
            raise UserStateException(
                "Cannot set the signature without both keys "
                "(id_key and pre_singed)"
            )
        return binascii.b2a_base64(
            self.id_key.exchange(self.signed_pre_key.public_key())
        )

    # Setters - had to invoke those methods for debugging purposes

    @login.setter
    def login(self, login):
        raise UserStateException(
            "Modyfying the user login is illegal!!! "
            "Try instead creating new instance of UserState"
        )

    @id_key.setter
    def id_key(self, new_id: X25519PrivateKey):
        """
        Args:
            new_id (str): encoded private keyin base64
        """
        self._id_key = new_id

    @signed_pre_key.setter
    def signed_pre_key(self, spk_key: X25519PrivateKey):
        self._signed_pre_key = spk_key

    @staticmethod
    def repr_private_key(key: Optional[X25519PrivateKey]):
        return create_b64_from_private_key(key) if key is not None else None

    def __repr__(self) -> str:
        return (
            f"Login: {self.login} | "
            f"Id_key: {UserState.repr_private_key(self.id_key)} | "
            "Signed_pre_key: "
            f"{UserState.repr_private_key(self.signed_pre_key)} | "
        )
