from enum import Enum
from pathlib import Path


# server constants
SERVER_URL = "ws://localhost:8001"
TABLE_SCHEMA_PATH = str(Path("app") / "database" / "schema.sql")
DEFAULT_DB_PATH = "user.db"

# other
PREFFERED_ENCODING = "utf-8"

# crypto constants
HASH_SALT = "made by wilkueti".encode(PREFFERED_ENCODING)  # NEVER DO THIS!!!
MAX_ONE_TIME_KEYS = 1
# length of the keyes is derived from the signal documentation
SHARED_KEY_LENGTH = 32
RATCHET_STATE_KEY_LENGTH = 64
# according to crypto library docs nonce should have 96 bits
AEAD_NONCE = "SEG0PPiuHAFm".encode(PREFFERED_ENCODING)
BLOCK_SIZE = 128

# usunąć
USER_DATA_PATH = "app/database/data.db <- look at this duud"


class MainMenuOptions(Enum):
    MESSAGE = 0
    ADD_FRIEND = 1
    CHANGE_CREDENTIALS = 2
    REMOVE_ACCOUNT = 3
    EXIT = 4
