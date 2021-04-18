from enum import Enum


SERVER_URL = "127.0.0.1:5000"
USER_DATA_PATH = "app/database/data.db"

class MainMenuOptions(Enum):
    MESSAGE = 0
    ADD_FRIEND = 1
    CHANGE_CREDENTIALS = 2
    REMOVE_ACCOUNT = 3
    EXIT=4