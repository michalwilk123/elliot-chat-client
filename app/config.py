from enum import Enum
from pathlib import Path

SERVER_URL = "127.0.0.1:5000"
TABLE_SCHEMA_PATH = Path("app") / "database" / "schema.sql"


# usunąć to na dole
USER_DATA_PATH = "app/database/data.db <- look at this duud"

class MainMenuOptions(Enum):
    MESSAGE = 0
    ADD_FRIEND = 1
    CHANGE_CREDENTIALS = 2
    REMOVE_ACCOUNT = 3
    EXIT=4