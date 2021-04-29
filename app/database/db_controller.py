from typing import List
from app.user_state import UserState
from app.config import TABLE_SCHEMA_PATH, DEFAULT_DB_PATH
import sqlite3
import os
import pickle
import codecs

class DatabaseControllerException(Exception):
    ...

class DatabaseController:
    def __init__(self, DB_PATH:str=DEFAULT_DB_PATH):
        self.DB_PATH = DB_PATH
        try:
            self.connection = sqlite3.connect(DB_PATH)
        except sqlite3.OperationalError:
            raise sqlite3.OperationalError(
                "Could not find the database path! \
                Make sure you passed the right path to the controller"
            )

        if not self.tables_exist():
            self.create_tables()

    def __del__(self):
        self.connection.close()

    def _reinstall(self):
        """delete and create an empty database"""
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

        # running constructor to create the database file from scratch
        self.__init__(DB_PATH=self.DB_PATH)

    def tables_exist(self) -> bool:
        cur = self.connection.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()

        cur.close()
        if tables is None:
            return False

        tables = set(map(lambda x: x[0], tables))
        return {"USERS", "CONTACTS"} == tables

    def create_tables(self):
        cur = self.connection.cursor()
        with open(TABLE_SCHEMA_PATH, "r") as table_file:
            cur.executescript(table_file.read())

        self.connection.commit()
        cur.close()

    # User crud operations

    def create_user(self, new_user_state: UserState):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO USERS (login, password) VALUES (?, ?)",
            (new_user_state.login, new_user_state.password),
        )
        self.connection.commit()
        cur.close()

    def user_exists(self, user_state: UserState) -> bool:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT login FROM USERS WHERE login=? AND password=?",
            (user_state.login, user_state.password),
        )
        res = cur.fetchone()
        cur.close()
        return res is not None

    def delete_user(self, user_state: UserState):
        if not self.user_exists(user_state):
            raise DatabaseControllerException("Cannot delete user which does not exist!!")

        cur = self.connection.cursor()

        cur.execute(
            "DELETE FROM USERS WHERE login=? AND password=?",
            (user_state.login, user_state.password),
        )
        self.connection.commit()
        cur.close()

    # Contacts crud operations

    def add_contact(self, state: UserState, contactLogin: str):
        if not self.user_exists(state):
            raise DatabaseControllerException("Cannot add contact to not existing user!!!")

        if state.login == contactLogin:
            raise DatabaseControllerException("Cannot add self to the contacts!!!")

        cur = self.connection.cursor()

        cur.execute(
            "INSERT INTO CONTACTS (owner, login) VALUES ( ?, ?)",
            (state.login, contactLogin),
        )

        self.connection.commit()
        cur.close()

    def delete_contact(self, user_state: UserState, contactLogin: str):
        if not self.contact_exists(user_state, contactLogin):
            raise DatabaseControllerException("Cannot delete not existing contact")

        cur = self.connection.cursor()
        cur.execute(
            "DELETE FROM CONTACTS WHERE owner=? AND login=?",
            (user_state.login, contactLogin),
        )
        self.connection.commit()
        cur.close()

    def contact_exists(self, user_state: UserState, contactLogin: str) -> bool:
        if not self.user_exists(user_state):
            raise DatabaseControllerException("Cannot check contacts of non-existing user!!!")

        cur = self.connection.cursor()
        cur.execute(
            "SELECT login FROM CONTACTS WHERE owner=? AND login=?",
            (user_state.login, contactLogin),
        )
        res = cur.fetchone()
        cur.close()
        return res is not None

    def get_user_contacts(self, state: UserState) -> List[str]:
        if not self.user_exists(state):
            raise DatabaseControllerException("Cannot get contacts of not existing user!!!")

        cur = self.connection.cursor()
        cur.execute("SELECT login FROM CONTACTS WHERE owner=?", (state.login,))
        results = cur.fetchall()
        print(results)
        cur.close()

        if results is None:
            return []

        return list(map(lambda x: x[0], results))
    

    def update_user_password(self, password:str):
        # TODO: create test case for this
        ...

    # --- Crypto stuff ---

    def get_user_send_ratchet(self, user:str, partner:str):
        return

    def get_user_recv_ratchet(self, user:str, partner:str):
        return

    
    def ratchets_correct(self, user:str, partner:str) -> bool:
        return True
    
    def load_user_keys(self, user_state:UserState) -> None:
        if not self.user_exists(user_state):
            raise DatabaseControllerException("Cannot load keys from not existing user")

        cur = self.connection.cursor()

        cur.execute(
            "SELECT id_key, signed_pre_key FROM USERS WHERE login=? AND password=?",
            (user_state.login, user_state.password,)
        )
        result = cur.fetchone()

        pickled_id_key = result[0]
        pickled_signed_pre_key = result[1]

        raw_id_key = pickle.loads(
            codecs.decode(pickled_id_key.encode(), "base64"))
        raw_signed_pre_key = pickle.loads(
            codecs.decode(pickled_signed_pre_key.encode(), "base64"))
        
        user_state.id_key = pickled_id_key
        user_state.id_key_pickled = pickled_signed_pre_key
        user_state.signed_pre_key = raw_id_key
        user_state.signed_pre_key_pickled = raw_signed_pre_key

        
    def update_user_keys(self, user_state:UserState) -> None:
        if user_state.id_key is None and user_state.signed_pre_key is None:
            raise DatabaseControllerException("why would you run this method if you dont do anything?")

        cur = self.connection.cursor()

        if user_state.id_key is None:
            id_key_pickled = codecs.encode(
                pickle.dumps(user_state.id_key), "base64").decode()
            cur.execute(
                "UPDATE USERS SET id_key=?", (id_key_pickled,)
            )

        if user_state.signed_pre_key is None:
            signed_pre_key_pickled = codecs.encode(
                pickle.dumps(user_state.signed_pre_key), "base64").decode()
            cur.execute(
                "UPDATE USERS SET signed_pre_key=?", (signed_pre_key_pickled,)
            )

        self.connection.commit()
        cur.close()

