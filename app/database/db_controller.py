from app.chat.crypto.ratchet_set import RatchetSet
from typing import List
from app.user_state import UserState
from app.config import TABLE_SCHEMA_PATH, DEFAULT_DB_PATH
from app.chat.crypto.crypto_utils import (
    create_b64_from_private_key,
    create_private_key_from_b64,
)
import sqlite3
import os


class DatabaseControllerException(Exception):
    ...


class DatabaseController:
    def __init__(self, DB_PATH: str = DEFAULT_DB_PATH):
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
            raise DatabaseControllerException(
                "Cannot delete user which does not exist!!"
            )

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
            raise DatabaseControllerException(
                "Cannot add contact to not existing user!!!"
            )

        if state.login == contactLogin:
            raise DatabaseControllerException(
                "Cannot add self to the contacts!!!"
            )

        cur = self.connection.cursor()

        cur.execute(
            "INSERT INTO CONTACTS (owner, login) VALUES ( ?, ?)",
            (state.login, contactLogin),
        )

        self.connection.commit()
        cur.close()

    def delete_contact(self, user_state: UserState, contactLogin: str):
        if not self.contact_exists(user_state, contactLogin):
            raise DatabaseControllerException(
                "Cannot delete not existing contact"
            )

        cur = self.connection.cursor()
        cur.execute(
            "DELETE FROM CONTACTS WHERE owner=? AND login=?",
            (user_state.login, contactLogin),
        )
        self.connection.commit()
        cur.close()

    def contact_exists(self, user_state: UserState, contactLogin: str) -> bool:
        if not self.user_exists(user_state):
            raise DatabaseControllerException(
                "Cannot check contacts of non-existing user!!!"
            )

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
            raise DatabaseControllerException(
                "Cannot get contacts of not existing user!!!"
            )
        cur = self.connection.cursor()
        cur.execute("SELECT login FROM CONTACTS WHERE owner=?", (state.login,))
        results = cur.fetchall()
        cur.close()

        if results is None:
            return []
        return list(map(lambda x: x[0], results))

    def update_user_password(self, password: str):
        # TODO: create test case for this
        ...

    # --- Crypto stuff ---

    def load_user_keys(self, user_state: UserState) -> None:
        if not self.user_exists(user_state):
            raise DatabaseControllerException(
                "Cannot load keys of not existing user"
            )

        cur = self.connection.cursor()

        cur.execute(
            "SELECT id_key, signed_pre_key FROM USERS "
            "WHERE login=? AND password=?",
            (
                user_state.login,
                user_state.password,
            ),
        )
        result = cur.fetchone()

        b64_id_key = result[0]
        b64_signed_pre_key = result[1]

        if b64_id_key is None or b64_signed_pre_key is None:
            raise DatabaseControllerException(
                "One of the keys is not present in the database. "
                "Try to check if you uploaded both: id key AND "
                "signed pre key. Without them both I cannot continue "
                "this operation :/"
            )

        id_key_obj = create_private_key_from_b64(b64_id_key)
        signed_pre_key_obj = create_private_key_from_b64(b64_signed_pre_key)

        user_state.id_key = id_key_obj
        user_state.id_key_b64 = b64_id_key
        user_state.signed_pre_key = signed_pre_key_obj
        user_state.signed_pre_key_b64 = b64_signed_pre_key

    def update_user_keys(self, user_state: UserState) -> None:
        if user_state.id_key is None and user_state.signed_pre_key is None:
            raise DatabaseControllerException(
                "why would you run this method if you dont do anything?"
            )

        cur = self.connection.cursor()

        if user_state.id_key is not None:
            id_key_b64 = create_b64_from_private_key(user_state.id_key)
            cur.execute(
                "UPDATE USERS SET id_key=? WHERE login=? AND password=?",
                (id_key_b64, user_state.login, user_state.password),
            )

        if user_state.signed_pre_key is not None:
            signed_pre_key_b64 = create_b64_from_private_key(
                user_state.signed_pre_key
            )
            cur.execute(
                "UPDATE USERS SET signed_pre_key=?"
                " WHERE login=? AND password=?",
                (signed_pre_key_b64, user_state.login, user_state.password),
            )

        self.connection.commit()
        cur.close()

    # --- RATCHETS STUFF

    def ratchets_present(self, user_state:UserState, contact:str) -> bool:
        """
        Check if database values of ratchets are not null
        """
        cur = self.connection.cursor()

        cur.execute(
            "SELECT send_ratchet, recv_ratchet, DH_ratchet FROM CONTACTS "\
                "WHERE owner=? AND login=?",
            (user_state.login, contact)
        )

        if cur is None:
            raise DatabaseControllerException(
                f"User does not have the contact {contact}!!"
            )

        return False if None in cur else True


    def load_ratchets(self, user_state:UserState, contact:str) -> RatchetSet:
        if not self.ratchets_present(user_state, contact):
            raise DatabaseControllerException(
                "You tried to load not exitsing ratchets!! Aborting immediately")

        ratchet_set = RatchetSet()

        cur = self.connection.cursor()
        cur.execute(
            "SELECT send_ratchet, recv_ratchet, DH_ratchet FROM CONTACTS "\
                "WHERE owner=? AND login=?",
            (user_state.login, contact)
        )
        result = cur.fetchone()

        ratchet_set.send_ratchet = result[0]
        ratchet_set.recv_ratchet = result[1]
        ratchet_set.dh_ratchet = result[2]

        cur.close()
        return ratchet_set


    def save_ratchets(self, user_state:UserState, contact:str, ratchet_set:RatchetSet) -> None:
        cur = self.connection.cursor()

        cur.execute(
            "SELECT shared_x3dh_key FROM CONTACTS WHERE owner=? AND login=?",
            (user_state.login, contact)
        )

    def get_chat_shared_key(self, user_state:UserState, contact:str) -> bytes:
        cur = self.connection.cursor()

        cur.execute(
            "SELECT shared_x3dh_key FROM CONTACTS WHERE owner=? AND login=?",
            (user_state.login, contact)
        )

        res = cur.fetchone()
        assert type(res) == bytes # sanity check
        cur.close()
        return res

