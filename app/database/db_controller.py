from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from app.chat.crypto.ratchet_set import RatchetSet
from typing import List, Optional, Tuple
from app.user.user_state import UserState
from app.config import TABLE_SCHEMA_PATH, DEFAULT_DB_PATH, MAX_ONE_TIME_KEYS
from app.chat.crypto.crypto_utils import (
    create_b64_from_private_key,
    create_private_key_from_b64,
    generate_DH,
)
import sqlite3
import os
import binascii


class DatabaseControllerException(Exception):
    ...


class ContactParametersError(Exception):
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
        res = {"USERS", "CONTACTS", "ONE_TIME_KEYS"} == tables

        if not res:
            os.remove(self.DB_PATH)
            self.connection.close()
            self.connection = sqlite3.connect(self.DB_PATH)

        return res

    def create_tables(self):
        cur = self.connection.cursor()
        with open(TABLE_SCHEMA_PATH, "r") as table_file:
            cur.executescript(table_file.read())

        self.connection.commit()
        cur.close()

    # User crud operations

    def create_user(self, user_state: UserState):
        cur = self.connection.cursor()
        user_state.id_key = generate_DH()
        user_state.signed_pre_key = generate_DH()

        cur.execute(
            "INSERT INTO USERS (login, id_key, signed_pre_key) "
            "VALUES (?, ?, ?)",
            (
                user_state.login,
                create_b64_from_private_key(user_state.id_key),
                create_b64_from_private_key(user_state.signed_pre_key),
            ),
        )

        for i in range(MAX_ONE_TIME_KEYS):
            otk = generate_DH()
            cur.execute(
                "INSERT INTO ONE_TIME_KEYS (key_index, owner, key) "
                "VALUES (?, ?, ?)",
                (
                    i,
                    user_state.login,
                    create_b64_from_private_key(otk),
                ),
            )

        self.connection.commit()
        cur.close()

    def user_exists(self, user_state: UserState) -> bool:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT login FROM USERS WHERE login=?",
            (user_state.login,),
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
            "DELETE FROM USERS WHERE login=?",
            (user_state.login,),
        )
        self.connection.commit()
        cur.close()

    # Contacts crud operations

    def add_contact(
        self,
        state: UserState,
        contactLogin: str,
        b64_id_key: str,
        shared_key: str,
        /,
        contact_signed_pre_key: Optional[str] = None,
        contact_ephemeral_key: Optional[str] = None,
        my_ephemeral_key: Optional[str] = None,
        contact_otk_key: Optional[str] = None,
        my_otk_key: Optional[str] = None,
    ) -> bool:
        if not self.user_exists(state):
            raise DatabaseControllerException(
                "Cannot add contact to not existing user!!!"
            )

        if state.login == contactLogin:
            raise DatabaseControllerException(
                "Cannot add self to the contacts!!!"
            )

        """
        The additional parameters can
        be added in only two ways:

            * Adding the establisher (aka this
            will be added if YOU send friend request to
            someone)
            {
                contact_signed_pre_key (public)
                my_emphemeral_key (private),
                contact_otk_key (public)
            }

            * Adding the guest (aka YOU opened app
            and you got pending friend request,
            this set of data will be then
            added)
            {
                contact_ephemeral_key (public),
                my_otk_key (private)
            }
        """

        if self.get_contact_info(state, contactLogin) is not None:
            return False

        # now checking if params are following above
        # specs
        if all(
            [
                contact_signed_pre_key is not None,
                my_ephemeral_key is not None,
                contact_otk_key is not None,
                # not set
                contact_ephemeral_key is None,
                my_otk_key is None,
            ]
        ):
            my_turn = True
        elif all(
            [
                contact_ephemeral_key is not None,
                my_otk_key is not None,
                # not set
                contact_signed_pre_key is None,
                my_ephemeral_key is None,
                contact_otk_key is None,
            ]
        ):
            my_turn = False
        else:
            raise ContactParametersError(
                "passed wrong combination of optional parameters!!"
            )

        cur = self.connection.cursor()

        # first we check if new contact acctually exists in the db
        # if yes than we rewrite and return false

        cur.execute(
            "INSERT INTO CONTACTS "
            "(owner, login, public_id_key, public_signed_pre_key, "
            "shared_x3dh_key, my_ephemeral_key, contact_ephemeral_key, "
            "my_otk_key, contact_otk_key, my_turn) "
            "VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                state.login,
                contactLogin,
                b64_id_key,
                contact_signed_pre_key,
                shared_key,
                my_ephemeral_key,
                contact_ephemeral_key,
                my_otk_key,
                contact_otk_key,
                int(my_turn),
            ),
        )

        self.connection.commit()
        cur.close()
        return True

    def get_contact_info(
        self, state: UserState, contact: str
    ) -> Optional[dict]:
        if not self.user_exists(state):
            raise DatabaseControllerException("Given user does not exist")

        cur = self.connection.cursor()

        cur.execute(
            "SELECT "
            "public_id_key, public_signed_pre_key, "
            "shared_x3dh_key, my_ephemeral_key, contact_ephemeral_key, "
            "my_otk_key, contact_otk_key "
            "FROM CONTACTS WHERE "
            "owner=? AND login=?",
            (state.login, contact),
        )

        res_tuple = cur.fetchone()
        cur.close()

        if res_tuple is None:
            return None

        result = {
            "login": contact,
            "public_id_key": res_tuple[0],
            "public_signed_pre_key": res_tuple[0],
            "shared_x3dh_key": res_tuple[1],
            "my_ephemeral_key": res_tuple[2],
            "contact_ephemeral_key": res_tuple[3],
            "my_otk_key": res_tuple[4],
            "contact_otk_key": res_tuple[5],
        }
        return result

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

    def get_user_otk(self, state: UserState) -> List[bytes]:
        if not self.user_exists(state):
            raise DatabaseControllerException(
                "Cannot get contacts of not existing user!!!"
            )
        cur = self.connection.cursor()
        cur.execute(
            "SELECT key FROM ONE_TIME_KEYS WHERE owner=?", (state.login,)
        )
        results = [el[0] for el in cur.fetchall()]
        return results

    # --- Crypto stuff ---

    def get_user_keys(
        self, user_state: UserState
    ) -> Tuple[X25519PrivateKey, X25519PrivateKey]:
        if not self.user_exists(user_state):
            raise DatabaseControllerException(
                "Cannot load keys of not existing user"
            )

        cur = self.connection.cursor()

        cur.execute(
            "SELECT id_key, signed_pre_key FROM USERS " "WHERE login=?",
            (user_state.login,),
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

        return id_key_obj, signed_pre_key_obj

    def set_user_keys(self, user_state: UserState) -> None:
        if user_state.id_key is None and user_state.signed_pre_key is None:
            raise DatabaseControllerException(
                "why would you run this method if you dont do anything?"
            )

        cur = self.connection.cursor()

        if user_state.id_key is not None:
            id_key_b64 = create_b64_from_private_key(user_state.id_key)
            cur.execute(
                "UPDATE USERS SET id_key=? WHERE login=?",
                (
                    id_key_b64,
                    user_state.login,
                ),
            )

        if user_state.signed_pre_key is not None:
            signed_pre_key_b64 = create_b64_from_private_key(
                user_state.signed_pre_key
            )
            cur.execute(
                "UPDATE USERS SET signed_pre_key=?" " WHERE login=?",
                (
                    signed_pre_key_b64,
                    user_state.login,
                ),
            )

        self.connection.commit()
        cur.close()

    # --- RATCHETS STUFF

    def ratchets_present(self, user_state: UserState, contact: str) -> bool:
        """
        Check if database values of ratchets are not null
        """
        cur = self.connection.cursor()

        cur.execute(
            "SELECT dh_ratchet, send_ratchet, recv_ratchet, root_ratchet "
            "FROM CONTACTS WHERE owner=? AND login=?",
            (user_state.login, contact),
        )

        res = cur.fetchone()
        if res is None:
            raise DatabaseControllerException(
                f"User does not have the contact {contact}!!"
            )

        return False if None in res else True

    def load_ratchets(self, user_state: UserState, contact: str) -> RatchetSet:
        if not self.ratchets_present(user_state, contact):
            raise DatabaseControllerException(
                "You tried to load not exitnot sing ratchets!! "
                "Aborting immediately"
            )

        ratchet_set = RatchetSet()

        cur = self.connection.cursor()
        cur.execute(
            "SELECT dh_ratchet, send_ratchet, recv_ratchet, root_ratchet "
            "FROM CONTACTS WHERE owner=? AND login=?",
            (user_state.login, contact),
        )
        result = cur.fetchone()
        ratchet_set.from_snapshot(*result[0:4])

        cur.close()
        return ratchet_set

    def save_ratchets(
        self,
        user_state: UserState,
        contact: str,
        ratchet_set: RatchetSet,
        my_turn: bool,
    ) -> None:
        cur = self.connection.cursor()

        cur.execute(
            "UPDATE CONTACTS "
            "SET dh_ratchet=?, send_ratchet=?, recv_ratchet=?, "
            "root_ratchet=?, my_turn=?"
            "WHERE owner=? AND login=?",
            (
                *ratchet_set.get_tuple(),
                int(my_turn),
                user_state.login,
                contact,
            ),
        )
        self.connection.commit()
        cur.close()

    def load_chat_init_variables(
        self, user_state: UserState, contact: str
    ) -> Tuple[bytes, bool]:
        cur = self.connection.cursor()
        cur.execute(
            "SELECT shared_x3dh_key, my_turn FROM CONTACTS "
            "WHERE owner=? AND login=?",
            (user_state.login, contact),
        )

        res = cur.fetchone()

        if res is None:
            raise DatabaseControllerException(
                f"User: {user_state.login}. ",
                f"Cannot find the contact of user {contact}",
            )
        cur.close()
        return binascii.a2b_base64(res[0]), bool(res[1])

    def save_chat_init_variables(
        self,
        user_state: UserState,
        contact: str,
        shared_key: bytes,
        turn: bool,
    ) -> None:
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE CONTACTS "
            "SET shared_x3dh_key=?, my_turn=? "
            "WHERE owner=? AND login=?",
            (
                binascii.b2a_base64(shared_key),
                int(turn),
                user_state.login,
                contact,
            ),
        )
        self.connection.commit()
        cur.close()

    def replace_one_time_key(
        self, user_state: UserState, index: int
    ) -> Tuple[X25519PrivateKey, X25519PrivateKey]:
        cur = self.connection.cursor()

        cur.execute(
            "SELECT key FROM ONE_TIME_KEYS WHERE key_index=? AND owner=?",
            (index, user_state.login),
        )

        result = cur.fetchone()

        if result is None:
            raise DatabaseControllerException(
                "Key at given index does not exist"
            )

        assert len(result) == 1, "There should be an unique key at given index"
        result = result[0]

        current_key = create_private_key_from_b64(result)
        new_one_time_key = generate_DH()

        cur.execute(
            "UPDATE ONE_TIME_KEYS SET key=? WHERE key_index=? AND owner=?",
            (
                create_b64_from_private_key(new_one_time_key),
                index,
                user_state.login,
            ),
        )
        self.connection.commit()
        cur.close()

        return current_key, new_one_time_key
