from typing import List
from app.user_state import UserState
import sqlite3

class DatabaseController:
    # TODO: IMPLEMENT THIS CLASS!!!
    def __init__(self, DB_PATH='db_data/user.db'):
        self.connection = sqlite3.connect(DB_PATH)

        if not self.file_correct():
            self._reinstall()

    def file_correct(self):
        ...

    def _reinstall(self):
        ...

    # User crud operations

    def create_user(self, new_user_state:UserState):
        ...

    def user_exists(self, user_state:UserState):
        ...

    def delete_user(self, user_state:UserState):
        ...

    # Contacts crud operations

    def add_contact(self, state:UserState, contactLogin:str):
        ...

    def delete_contact(self, user_state:UserState, contactLogin:str):
        ...

    def contact_exists(self, user_state:UserState, contactLogin:str):
        ...

    def get_user_contacts(self, state:UserState) -> List[str]:
        return
    