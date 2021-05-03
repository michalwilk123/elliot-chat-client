from typing import Optional
from .crypto.inner_ratchet import InnerRatchet
from .crypto.ratchet_set import RatchetSet, RatchetSetException
from .crypto.crypto_utils import (
    aead_decrypt,
    aead_encrypt,
    generate_DH,
)
from app.user_state import UserState
from app.config import DEFAULT_DB_PATH
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.exceptions import InvalidTag
from app.database.db_controller import DatabaseController


class ChatMemberException(Exception):
    ...


class ChatMember:
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

    def init_ratchets(self):
        """
        Checks if old ratchets are present. If not
        """

        db_controller = DatabaseController(DB_PATH=self.db_path)

        if db_controller.ratchets_present(self.user_state, self.contact):
            self.ratchet_set = db_controller.load_ratchets(
                self.user_state, self.contact
            )
        else:
            # this will run for the first time the users are connected
            shared_key, my_turn = db_controller.load_chat_init_variables(
                self.user_state, self.contact
            )
            if self.my_turn is not None:
                self.my_turn = my_turn

            self.initialize_symmertic_ratchets(shared_key)

    def get_ratchet_set(self) -> RatchetSet:
        return self.ratchet_set

    def initialize_symmertic_ratchets(self, shared_key: bytes) -> None:
        """
        Initializing symmetric ratchets:
            send_ratchet, recv_ratchet, root_ratchet
            Order of initializing depends on which user
            initialized the chat first
        """
        r_set = RatchetSet()
        r_set.root_ratchet = InnerRatchet(shared_key)

        if self.my_turn:
            """
            If it is our turn to initialize ratchets we create
            at the start the SEND RATCHET AND THEN RECV RATCHET
            """
            r_set.send_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])
            r_set.recv_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])
        else:
            r_set.recv_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])
            r_set.send_ratchet = InnerRatchet(r_set.root_ratchet.turn()[0])
            r_set.dh_ratchet = generate_DH()
            self.my_turn = True

        self.ratchet_set = r_set

    def rotate_dh_ratchet(self, public_key: X25519PublicKey) -> None:
        if not self.my_turn:
            raise ChatMemberException(
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
        public_key: X25519PublicKey = None,
        initial: bool = False,
    ) -> bytes:
        if initial:
            if public_key is not None:
                self.rotate_dh_ratchet(public_key)
            else:
                raise ChatMemberException(
                    "Cannot initiate DH ratchet rotation "
                    "without dh public key!!"
                )
        root_key, chain_key = self.ratchet_set.recv_ratchet.turn()

        try:
            decrypted_message = aead_decrypt(root_key, message, chain_key)
        except InvalidTag:
            raise ChatMemberException(
                "You passed bad key for decryption! ",
                "Check if your ratchets are synchronized correctly!!",
            )

        return decrypted_message

    def get_dh_public_key(self):
        return self.ratchet_set.dh_ratchet.public_key()
