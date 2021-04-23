from typing import List
from app.user_state import UserState
from app.config import TABLE_SCHEMA_PATH
import sqlite3
import os

class DatabaseController:
    # TODO: IMPLEMENT THIS CLASS!!!
    def __init__(self, DB_PATH='db_data/user.db'):
        self.DB_PATH = DB_PATH
        try:
            self.connection = sqlite3.connect(DB_PATH)
        except sqlite3.OperationalError:
            raise sqlite3.OperationalError(
                "Could not find the database path! \
                Make sure you passed the right path to the controller")
        
        if not self.tables_exist():
            self.create_tables()

    def _reinstall(self):
        """delete and create an empty database
        """
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)
        self.__init__(DB_PATH=self.DB_PATH)


    def tables_exist(self) -> bool:
        cur = self.connection.cursor()

        cur.execute(
            "SELECT * FROM tablename;"
        )
        tables = set(cur.fetchall())
        print(tables)
        cur.close()
        return False

    def create_tables(self):
        cur = self.connection.cursor()
        with open(TABLE_SCHEMA_PATH, "r") as table_file:
            cur.executemany(table_file.read())
        
        cur.commit()
        cur.close()
        

    # User crud operations

    def create_user(self, new_user_state:UserState):
        cur = self.connection.cursor()
        cur.execute("")
        cur.close()

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
    