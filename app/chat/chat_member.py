from app.chat.crypto.inner_ratchet import InnerRatchet
from app.chat.crypto.ratchet_set import RatchetSet
from app.user_state import UserState
from app.config import DEFAULT_DB_PATH 

class ChatMember:
    """
    Chat member which has all the 
    ratchets and ecrypts / decrypts messages
    """
    def __init__(self, user_state: UserState, contact:str, my_turn:bool, /, DB_PATH=DEFAULT_DB_PATH) -> None:
        self.user_state = user_state
        self.my_turn = my_turn
        self.contact = contact
        self.db_path = DB_PATH


    def init_ratchets(self):
        """
        Checks if old ratchets are present. If not
        """
        from app.database.db_controller import DatabaseController
        db_controller = DatabaseController(DB_PATH=self.db_path)

        if db_controller.ratchets_present(self.user_state, self.contact):
            self.ratchet_set = db_controller.load_ratchets(self.user_state, self.contact)
        else:
            # this will run for the first time the users are connected
            shared_key = db_controller.get_chat_shared_key(
                self.user_state, self.contact)
            self.initialize_symmertic_ratchets(shared_key)
            

    def get_ratchet_set(self) -> RatchetSet:
        return self.ratchet_set

    def initialize_symmertic_ratchets(self, shared_key:bytes):
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

        self.ratchet_set = r_set
