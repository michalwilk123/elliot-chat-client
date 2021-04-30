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

def test_ratchet_set():
    # check if all getters and setters are running correctly. Sanity check
    rset = RatchetSet()
    ir_recv = InnerRatchet(token_bytes(SHARED_KEY_LENGTH))
    ir_send = InnerRatchet(token_bytes(SHARED_KEY_LENGTH))
    ir_root = InnerRatchet(token_bytes(SHARED_KEY_LENGTH))
    ir_dh = InnerRatchet(token_bytes(SHARED_KEY_LENGTH))

    rset.recv_ratchet = ir_recv
    rset.send_ratchet = ir_send
    rset.root_ratchet = ir_root
    rset.dh_ratchet = ir_dh 

    assert rset.recv_ratchet.get_snapshot() == ir_recv.get_snapshot()
    assert rset.send_ratchet.get_snapshot() == ir_send.get_snapshot()
    assert rset.root_ratchet.get_snapshot() == ir_root.get_snapshot()
    assert rset.dh_ratchet.get_snapshot() == ir_dh .get_snapshot()

def test_initialize_ratchets(mocker):
    """
    Integrity test:
        Testing parameters of ratchets throughout
        the app initialization
    """
    alice_state = UserState("alice", "password")
    alice_clone_state = UserState("alice_clone", "dnsajkndjksan")

    alice_chat = ChatMember(alice_state, "dsnkjdsnak", True)
    alice_clone_chat = ChatMember(alice_clone_state, "cnxzcxzbcmz", True)
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    """ 
    fabrication of the alice clone ratchets.
    """
    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=True
    )

    test_ratchet_set = RatchetSet()
    inner_root = InnerRatchet(exp_shared_key)

    test_ratchet_set.root_ratchet = inner_root
    test_ratchet_set.send_ratchet = InnerRatchet(inner_root.turn()[0])
    test_ratchet_set.recv_ratchet = InnerRatchet(inner_root.turn()[0])

    mocker.patch(
        "app.database.db_controller.DatabaseController.load_ratchets",
        return_value= test_ratchet_set
    )
    alice_clone_chat.init_ratchets()
    alice_clone_r_set =  alice_clone_chat.get_ratchet_set()

    """Now we allow original alice to create her ratchets as she would
     normally do 
    """
    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False # Value here changes !!
    )
    mocker.patch(
        "app.database.db_controller.DatabaseController.get_chat_shared_key",
        return_value=exp_shared_key # Value here changes !!
    )
    alice_chat.init_ratchets()
    alice_r_set = alice_chat.get_ratchet_set()

    assert alice_clone_r_set.root_ratchet.get_snapshot() == alice_r_set.root_ratchet.get_snapshot()
    assert alice_clone_r_set.send_ratchet.get_snapshot() == alice_r_set.send_ratchet.get_snapshot()
    assert alice_clone_r_set.recv_ratchet.get_snapshot() == alice_r_set.recv_ratchet.get_snapshot()


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


def test_dh_ratchet_creation():
    assert False