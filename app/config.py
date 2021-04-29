from enum import Enum
from pathlib import Path

SERVER_URL = "ws://localhost:8001"
TABLE_SCHEMA_PATH = str(Path("app") / "database" / "schema.sql")
DEFAULT_DB_PATH = str(Path("db_data") / "user.db")
HASH_SALT = "made by wilkueti".encode("utf-8")  # NEVER DO THIS!!!
MAX_ONE_TIME_KEYS = 1

# usunąć
USER_DATA_PATH = "app/database/data.db <- look at this duud"


class MainMenuOptions(Enum):
    MESSAGE = 0
    ADD_FRIEND = 1
    CHANGE_CREDENTIALS = 2
    REMOVE_ACCOUNT = 3
    EXIT = 4
