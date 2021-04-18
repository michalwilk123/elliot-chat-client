from __future__ import annotations
from app.config import SERVER_URL, USER_DATA_PATH
from app.user.current_user import CurrentUser
import requests
import os
import sqlite3

class UserLoader:
    def load_user_data(current_user:CurrentUser):
        """
        loads user data if it exists if not,
        asks for informations at startup
        """
        if not os.path.exists(USER_DATA_PATH):
            UserLoader.__create_tables()

        # testowanie czy uzytkownik istnieje w bazie


    def check_connection() -> bool:
        """
        Test if connection with the server exists
        """
        resp = requests.get(SERVER_URL)
        return resp.status_code == 200
    

    @staticmethod
    def __create_tables():
        ...
