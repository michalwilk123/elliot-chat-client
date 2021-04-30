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
# according to crypto library docs nonce should have 96 bits
AEAD_NONCE = (
    b"4d99420692e1e7d1437f8f669543be8f9ee66142c7028"
    b"03cfb9ab52c2e2e1cb984af21d94af4ca2309d889057801"
    b"f119dabe168125b1b0ed3e6e4e2946e354eb7cfb2a12f73"
    b"89a0bb7a0e85cfea80790e70267dffa7ec497dcb8c6c78b096bea"
)

# usunąć
USER_DATA_PATH = "app/database/data.db <- look at this duud"


class MainMenuOptions(Enum):
    MESSAGE = 0
    ADD_FRIEND = 1
    CHANGE_CREDENTIALS = 2
    REMOVE_ACCOUNT = 3
    EXIT = 4
