from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from app.user_state import UserState
from app.database.db_controller import DatabaseController
from .crypto_utils import generate_private_key, hkdf
from app.config import DEFAULT_DB_PATH


class Guest:
    def __init__(
        self,
        user_state: UserState,
        /,
        id_key=None,
        DB_PATH: str = DEFAULT_DB_PATH,
        load_from_db: bool = False,
    ):
        """
        This instance is created per user add.
        Creating ephemeral key:
        """
        self.user_state = user_state
        self.db_path = DB_PATH

        if load_from_db:
            self.load()

        if not load_from_db and self.user_state.id_key is None:
            self.user_state.id_key = generate_private_key()
        
        if not load_from_db and self.user_state.signed_pre_key is None:
            self.user_state.signed_pre_key = generate_private_key()

        # ephemeral key is ALWAYS reacreated per contact add
        self.ephemeral_key = generate_private_key()

    def save(self):
        db_controller = DatabaseController(DB_PATH=self.db_path)
        db_controller.update_user_keys(self.user_state)
        del db_controller

    def load(self):
        db_controller = DatabaseController(DB_PATH=self.db_path)
        db_controller.load_user_keys(self.user_state)
        del db_controller

    def get_public_id_key(self) -> X25519PublicKey:
        return self.user_state.id_key.public_key()

    def get_public_ephemeral_key(self) -> X25519PublicKey:
        return self.ephemeral_key.public_key()

    def create_shared_key_X3DH(
        self,
        id_key: X25519PublicKey,
        signed_prekey: X25519PublicKey,
        one_time_key: X25519PublicKey,
    ) -> None:

        """the 4 diffie hellman key exchange
        from the perspective of someone who is an
        initiator of the conversation
        """
        dh1 = self.user_state.id_key.exchange(signed_prekey)
        dh2 = self.ephemeral_key.exchange(id_key)
        dh3 = self.ephemeral_key.exchange(signed_prekey)
        dh4 = self.ephemeral_key.exchange(one_time_key)

        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.shared_key = hkdf(dh1 + dh2 + dh3 + dh4, 32)

    def get_shared_key(self):
        if hasattr(self, "shared_key"):
            return self.shared_key
        return None
