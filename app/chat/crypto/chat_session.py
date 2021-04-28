"""This class is preffered way to encypt and decrypt messages
"""
from app.database.db_controller import DatabaseController
from app.config import DEFAULT_DB_PATH

class ChatSession:
    """This class is responsible for
    connection with users already present in session. 
    Implements ratchets and actually encrypts and 
    decrypts incoming and recieving messages!!!
    """
    def __init__(self, user:str, partner:str, DB_PATH:str=DEFAULT_DB_PATH):
        self.db_controller = DatabaseController(DB_PATH)
        self.user = user
        if not self.db_controller.ratchets_correct():
            self.create_ratchets()
            self.save_ratchets()

        self.send_ratchet = self.db_controller\
            .get_user_send_ratchet(user, partner)
        self.recv_ratchet = self.db_controller
            .get_user_recv_ratchet(user, partner)


    def enrypt_sending(self, raw_message:str) -> str:
        """Ecrypts readable message into url safe 
        encrypted string. Changes state of internal ratchets !

        Args:
            raw_message (str): [description]
        """
        ...


    def decrypt_recieved(self, enc_message:str) -> str:
        """
        Decrypts message and changes state of the
        internal ratchets
        Args:
            enc_message (str): non readable encrypted 
                message recieved by the server

        Returns:
            str: readable, decrypted message
        """
        ...


    def create_ratchets(self):
        ...

    def save_ratchets(self):
        ...