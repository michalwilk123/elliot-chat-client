from app.user_state import UserState
from app.database.db_controller import DatabaseController
from .crypto_utils import generate_private_key, hkdf
from app.config import DEFAULT_DB_PATH

class Guest:
    def __init__(self, user_state:UserState, /, id_key=None, DB_PATH:str=DEFAULT_DB_PATH, load_from_db:bool=False):
        """
        This instance is created per user add.
        Creating ephemeral key:
        """
        self.user_state = user_state
        self.db_path = DB_PATH

        if load_from_db:
            self.load()
        elif id_key is None:
            self.user_state.id_key = generate_private_key()
            self.save()

        self.id_key = id_key
        # ephemeral key is ALWAYS reacreated per app launch
        self.ephemeral_key = generate_private_key()

    def save(self):
        db_controller = DatabaseController(self.db_path)
        db_controller.update_user_keys(self.user_state)
        del db_controller

    def load(self):
        db_controller = DatabaseController(self.db_path)
        db_controller.load_user_keys(self.user_state)
        del db_controller

    
    def get_public_id_key(self):
        return self.id_key.generate()

    def get_public_ephemeral_key(self):
        return self.ephemeral_key.generate()

    def create_shared_key_X3DH(self, id_key, signed_prekey, one_time_key) -> None:

        """the 4 diffie hellman key exchange
        from the perspective of someone who is an
        initiator of the conversation
        """
        dh1 = self.id_key.exchange(signed_prekey)
        dh2 = self.ephemeral_key.exchange(id_key)
        dh3 = self.ephemeral_key.exchange(signed_prekey)
        dh4 = self.ephemeral_key.exchange(one_time_key)

        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.shared_key = hkdf(dh1 + dh2 + dh3 + dh4, 32)

    def get_shared_key(self):
        if hasattr(self, "shared_key"):
            return self.shared_key
        return None

    def choose_external_otk(self, login:str):
        return 0, generate_private_key()