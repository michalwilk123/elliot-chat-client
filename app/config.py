from enum import Enum
from pathlib import Path

SERVER_URL = "ws://localhost:8001"
TABLE_SCHEMA_PATH = Path("app") / "database" / "schema.sql"


# usunąć
USER_DATA_PATH = "app/database/data.db <- look at this duud"

class MainMenuOptions(Enum):
    MESSAGE = 0
    ADD_FRIEND = 1
    CHANGE_CREDENTIALS = 2
    REMOVE_ACCOUNT = 3
    EXIT=4