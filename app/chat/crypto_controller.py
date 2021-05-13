from typing import Optional
from .crypto.inner_ratchet import InnerRatchet
from .crypto.ratchet_set import RatchetSet, RatchetSetException
from .crypto.crypto_utils import (
    aead_decrypt,
    aead_encrypt,
    create_b64_from_public_key,
    create_public_key_from_b64,
    generate_DH,
)
from app.user.user_state import UserState
from app.config import DEFAULT_DB_PATH, PREFFERED_ENCODING
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.exceptions import InvalidTag
from app.database.db_controller import DatabaseController
from app.api.response_type import ResponseType
import binascii
from time import time


class CryptoControllerException(Exception):
    ...


class CryptoController:
    """
    Chat member which has all the
    ratchets and ecrypts / decrypts messages
    """

    def __init__(
        self,
        user_state: UserState,
        contact: str,
        /,
        my_turn: Optional[bool] = None,
        DB_PATH=DEFAULT_DB_PATH,
    ) -> None:
        self.user_state = user_state
        """
        The my_turn variable makes sure that all ratchets are synchronized
        The program aborts immiedatly when this variable will contain
        not expected value !
        """
        self.my_turn = my_turn
        self.contact = contact
        self.db_path = DB_PATH

    def init_ratchets(
        self,
        /,
        opt_public_key: Optional[X25519PublicKey] = None,
        opt_private_key: Optional[X25519PrivateKey] = None,
    ):
        """
        Checks if old ratchets are present. If not it creates them
        for later use
        """

        db_controller = DatabaseController(DB_PATH=self.db_path)

        if db_controller.ratchets_present(self.user_state, self.contact):
            self.ratchet_set = db_controller.load_ratchets(
                self.user_state, self.contact
            )
            assert (
                opt_private_key is None and opt_public_key is None
            ), "You should not preemptively turn when you initialized"
        else:
            # this will run for the first time the users are connected
            shared_key, my_turn = db_controller.load_chat_init_variables(
                self.user_state, self.contact
            )
            if self.my_turn is not None:
                self.my_turn = my_turn
            else:
                self.my_turn = my_turn

            self.initialize_symmertic_ratchets(
                shared_key,
                opt_public_key=opt_public_key,
                opt_private_key=opt_private_key,
            )

    def get_ratchet_set(self) -> RatchetSet:
        return self.ratchet_set

    def initialize_symmertic_ratchets(
        self,
        shared_key: bytes,
        /,
        opt_public_key: Optional[X25519PublicKey] = None,
        opt_private_key: Optional[X25519PrivateKey] = None,
    ) -> None:
        """
        Initializing symmetric ratchets:
            send_ratchet, recv_ratchet, root_ratchet
            Order of initializing depends on which user
            initialized the chat first
        """
        r_set = RatchetSet()
        r_set.root_ratchet = InnerRatchet(shared_key)

        assert (
            self.my_turn is not None
        ), "The order of intitialization must be resolved"

        if self.my_turn:
            """
            If it is our turn to initialize ratchets we create
            at the start the SEND RATCHET AND THEN RECV RATCHET
            """
            r_set.send_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])
            r_set.recv_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])

            # initializing preemptive turn
            if opt_public_key is not None:
                self.ratchet_set = r_set
                self.rotate_dh_ratchet(opt_public_key)

            assert opt_private_key is None, "Bad initialization!!"
        else:
            r_set.recv_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])
            r_set.send_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])
            self.my_turn = True

            if opt_private_key is not None:
                r_set.dh_ratchet = opt_private_key
            else:
                r_set.dh_ratchet = generate_DH()
            assert opt_public_key is None, "Bad initialization!!"

        self.ratchet_set = r_set

    def rotate_dh_ratchet(self, public_key: X25519PublicKey) -> None:
        if not self.my_turn:
            raise CryptoControllerException(
                "SYNCHORNIZATION ERROR!! Detected double "
                "turn when decrypting!! Aborting..."
            )
        self.my_turn = False

        try:
            recieving_secret = self.ratchet_set.dh_ratchet.exchange(public_key)
            shared_recv_secret = self.ratchet_set.root_ratchet.turn(
                recieving_secret
            )[0]
            self.ratchet_set.recv_ratchet = InnerRatchet(shared_recv_secret)
        except RatchetSetException:
            ...

        self.ratchet_set.dh_ratchet = X25519PrivateKey.generate()
        sending_secret = self.ratchet_set.dh_ratchet.exchange(public_key)
        shared_send_secret = self.ratchet_set.root_ratchet.turn(
            sending_secret
        )[0]
        self.ratchet_set.send_ratchet = InnerRatchet(shared_send_secret)

    def encrypt(self, message: bytes) -> bytes:
        self.my_turn = True
        root_key, chain_key = self.ratchet_set.send_ratchet.turn()
        ecrypted_plaintext = aead_encrypt(root_key, message, chain_key)
        return ecrypted_plaintext

    def decrypt(
        self,
        message: bytes,
        /,
        public_key: Optional[X25519PublicKey] = None,
    ) -> bytes:
        if public_key is not None:
            self.rotate_dh_ratchet(public_key)
        else:
            assert (
                public_key is None
            ), "Passed the public key without any reason"

        root_key, chain_key = self.ratchet_set.recv_ratchet.turn()

        try:
            decrypted_message = aead_decrypt(root_key, message, chain_key)
        except InvalidTag:
            raise CryptoControllerException(
                "You passed bad key for decryption! ",
                "Check if your ratchets are synchronized correctly!!",
            )

        return decrypted_message

    def get_dh_public_key(self):
        return self.ratchet_set.dh_ratchet.public_key()

    """
    Message object template:

    {
        "head" : {
            "message_type" : TEXT_MESSAGE
            "sender" : "user123"
            "posix_time_send" : 321321
        },
        "body" : {
            "content" : "dsakjndksak"
            "public_key" : b64 key
        }
    }
    """

    def encrypt_to_json_message(self, plaintext: str) -> dict:
        encrypted = self.encrypt(plaintext.encode(PREFFERED_ENCODING))
        msg_to_send = {
            "head": {
                "message_type": ResponseType.TEXT_MESSAGE,
                "sender": self.user_state.login,
                "posix_time_send": int(time()),
            },
            "body": {
                "content": binascii.b2a_base64(encrypted),
                "public_key": create_b64_from_public_key(
                    self.get_dh_public_key()
                ),
            },
        }
        return msg_to_send

    def decrypt_json_message(self, message: dict) -> str:
        header = message["head"]
        body = message["body"]

        if header["sender"] != self.contact:
            raise CryptoControllerException(
                f"Wrong contact! I thought that I was communicating "
                f"with {self.contact} and not {header['sender']}"
            )

        if header["message_type"] == ResponseType.TEXT_MESSAGE:
            decr_msg = self.decrypt(
                binascii.a2b_base64(body["content"]),
                public_key=create_public_key_from_b64(body["public_key"])
                if self.my_turn
                else None,
            )
            return decr_msg.decode(PREFFERED_ENCODING)
        else:
            raise NotImplementedError(
                "I do not know what to do with this type of message"
            )
