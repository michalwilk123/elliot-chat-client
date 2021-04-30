from app.chat.crypto.establisher import Establisher
from app.chat.crypto.guest import Guest
from app.user_state import UserState
from app.database.db_controller import DatabaseController
from secrets import token_bytes
from app.config import SHARED_KEY_LENGTH
from app.chat.crypto.inner_ratchet import InnerRatchet
from app.chat.chat_member import ChatMember
from app.chat.crypto.ratchet_set import RatchetSet

TEST_DB_PATH = "test_user.db"

def test_ratchet_creation():
    assert True

def test_initialize_ratchets(mocker):
    """
    Integrity test:
        Testing parameters of ratchets throughout
        the app initialization
    """
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=True
    )
    bob = ChatMember(bob_state, "mocked_alice", False)

    test_ratchet_set = RatchetSet()
    inner_root = InnerRatchet(exp_shared_key)

    test_ratchet_set.send_ratchet = InnerRatchet(inner_root.turn()[0])
    test_ratchet_set.recv_ratchet = InnerRatchet(inner_root.turn()[0])


    mocker.patch(
        "app.database.db_controller.DatabaseController.load_ratchets",
        return_value= test_ratchet_set
    )
    alice = ChatMember(alice_state, "mocked_bob", True)

    """
    Alice gets mocked ratchets and we will compare them 
    to Bob's ratchets
    """

    alice_set = alice.get_ratchet_set()
    bob_set = bob.get_ratchet_set()

    bob_set.dh_ratchet = alice_set.dh_ratchet
    assert alice_set == bob_set


def test_initialize_symmetric_ratchets():
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    alice = ChatMember(alice_state, "ewiqoeoiq", True)
    bob = ChatMember(bob_state, "alicejksndka", False)

    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    alice_r_set = alice.get_ratchet_set()
    bob_r_set = bob.get_ratchet_set()

    assert alice_r_set.recv_ratchet.turn() == bob_r_set.send_ratchet.turn()
    assert bob_r_set.recv_ratchet.turn() == alice_r_set.send_ratchet.turn()