from enum import Enum
from pathlib import Path


# server constants
SERVER_URL = "ws://localhost:8001"
TABLE_SCHEMA_PATH = str(Path("app") / "database" / "schema.sql")
DEFAULT_DB_PATH = str(Path("db_data") / "user.db")


# crypto constants
HASH_SALT = "made by wilkueti".encode("utf-8")  # NEVER DO THIS!!!
MAX_ONE_TIME_KEYS = 1
# length of the keyes is derived from the signal documentation
SHARED_KEY_LENGTH = 32
RATCHET_STATE_KEY_LENGTH = 64
# according to signal docs nonce should have 128 bits of entropy
AEAD_NONCE = 2137

# usunąć
USER_DATA_PATH = "app/database/data.db <- look at this duud"


class MainMenuOptions(Enum):
    MESSAGE = 0
    ADD_FRIEND = 1
    CHANGE_CREDENTIALS = 2
    REMOVE_ACCOUNT = 3
    EXIT = 4
