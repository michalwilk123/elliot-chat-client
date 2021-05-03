from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from typing import Union, Optional


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

    __slots__ = (
        "_login",
        "_password",
        "_id_key",
        "_signed_pre_key",
        "_id_key_b64",
        "_signed_pre_key_b64",
    )

    def __init__(self, login: str, password: str):
        self._login: str = login
        self._password: str = password
        self._id_key_b64: Optional[bytes] = None
        self._signed_pre_key_b64: Optional[bytes] = None
        self._id_key: Optional[X25519PrivateKey] = None
        self._signed_pre_key: Optional[X25519PrivateKey] = None

    @property
    def login(self) -> str:
        return self._login

    @property
    def password(self) -> str:
        return self._password

    @property
    def id_key(self) -> Optional[X25519PrivateKey]:
        return self._id_key

    @property
    def signed_pre_key(self) -> Optional[X25519PrivateKey]:
        return self._signed_pre_key

    @property
    def id_key_b64(self) -> bytes:
        if self._id_key_b64 is None:
            raise UserStateException(
                "Cannot access base64 encoded private id key, "
                "because it is not present!!"
            )
        return self._id_key_b64

    @property
    def signed_pre_key_b64(self) -> bytes:
        if self._signed_pre_key_b64 is None:
            raise UserStateException("Private id key not initialized")
        return self._signed_pre_key_b64

    # Setters - had to invoke those methods for debugging purposes

    @login.setter
    def login(self, login):
        raise UserStateException(
            "Modyfying the user login is illegal!!! "
            "Try instead creating new instance of UserState"
        )

    @password.setter
    def password(self, password: str):
        self._password = password

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

    @id_key_b64.setter
    def id_key_b64(self, new_id: bytes):
        """
        Args:
            new_id (str): encoded private keyin base64
        """
        self._id_key_b64 = new_id

    @signed_pre_key_b64.setter
    def signed_pre_key_b64(self, spk_key: bytes):
        self._signed_pre_key_b64 = spk_key

    def __repr__(self) -> str:
        """NEVER DO THIS!!! VERY BAD PRACTICE !!"""
        return (
            f"Login: {self.login} | Password: {self.password} | "
            f"Id_key: {self.id_key} | Signed_pre_key: {self.signed_pre_key} | "
            f"Id_key_b64: {self.id_key_b64} | Signed_pre_key_b64: "
            f"{self.signed_pre_key_b64}"
        )
