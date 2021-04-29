from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


class UserStateException(Exception):
    ...


class UserState:
    """
    Current informations about the app state.
    This functionality is based on redux state class.
    Using slots because atributes in this class will be accessed
    quite frequently
    """

    # __slots__ = "login", "password", "id_key", "signed_pre_key", "id_key_pickled", "signed_pre_key_pickled"\
    #     "_login", "_password", "_id_key", "_signed_pre_key", "_id_key_pickled", "_signed_pre_key_pickled"

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
        self._id_key_b64: str = ""
        self._signed_pre_key_b64: str = ""

    @property
    def login(self) -> str:
        return self._login

    @property
    def password(self) -> str:
        return self._password

    @property
    def id_key(self) -> X25519PrivateKey:
        return self._id_key

    @property
    def signed_pre_key(self) -> X25519PrivateKey:
        return self._signed_pre_key

    @property
    def id_key_b64(self) -> str:
        return self._id_key_pickled

    @property
    def signed_pre_key_b64(self) -> str:
        return self._signed_pre_key_pickled

    # Setters - had to invoke those methods for debugging purposes

    @login.setter
    def login(self, login):
        raise UserStateException(
            "Modyfying the user login is illegal!!! Try instead creating new instance of UserState"
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
    def id_key_b64(self, new_id: str):
        """
        Args:
            new_id (str): encoded private keyin base64
        """
        self._id_key_pickled = new_id

    @signed_pre_key_b64.setter
    def signed_pre_key_b64(self, spk_key: str):
        self._signed_pre_key_pickled = spk_key
