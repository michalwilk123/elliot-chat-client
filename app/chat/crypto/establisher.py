from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
from app.user_state import UserState
from .crypto_utils import generate_private_key, hkdf
from app.config import MAX_ONE_TIME_KEYS, DEFAULT_DB_PATH
from app.database.db_controller import DatabaseController


class Establisher:
    def __init__(
        self,
        user_state: UserState,
        /,
        id_key=None,
        signed_pre_key=None,
        DB_PATH: str = DEFAULT_DB_PATH,
        load_from_db: bool = False,
    ):
        """
        This is created once per app runtime
        """
        self.db_path = DB_PATH

        if load_from_db:
            self.user_state = user_state
            self.load()
            return

        if id_key is None:
            user_state.id_key = generate_private_key()

        if signed_pre_key is None:
            user_state.signed_pre_key = generate_private_key()

        self.user_state = user_state

    def set_one_time_key(self, index: int):
        """Fetches one time key chosen by the guest,
        deletes it and creates new one for its place
        Returns:
        """
        """The one time key exists for very limited time
        so we DO NOT save in the user_state class
        """
        self.one_time_key = generate_private_key()
        # TODO: DELETE THE ONE TIME KEY AT THIS MOMENT

    def get_shared_key(self):
        if hasattr(self, "shared_key"):
            return self.shared_key
        return None

    def save(self):
        db_controller = DatabaseController(DB_PATH=self.db_path)
        db_controller.update_user_keys(self.user_state)
        del db_controller

    def load(self):
        db_controller = DatabaseController(DB_PATH=self.db_path)
        db_controller.load_user_keys(self.user_state)
        del db_controller

    def create_shared_key_X3DH(
        self, id_key: X25519PublicKey, ephemeral_key: X25519PublicKey
    ) -> None:
        dh1 = self.user_state.signed_pre_key.exchange(id_key)
        dh2 = self.user_state.id_key.exchange(ephemeral_key)
        dh3 = self.user_state.signed_pre_key.exchange(ephemeral_key)
        dh4 = self.one_time_key.exchange(ephemeral_key)

        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.shared_key = hkdf(dh1 + dh2 + dh3 + dh4, 32)

    def get_public_id_key(self) -> X25519PublicKey:
        return self.user_state.id_key.public_key()

    def get_public_signed_key(self) -> X25519PublicKey:
        return self.user_state.signed_pre_key.public_key()

    def get_public_one_time_key(self) -> X25519PublicKey:
        return self.one_time_key.public_key()
