from app.user_state import UserState
from secrets import token_bytes
from app.config import PREFFERED_ENCODING, SHARED_KEY_LENGTH
from app.chat.crypto.inner_ratchet import InnerRatchet
from app.chat.chat_member import ChatMember, ChatMemberException
from app.chat.crypto.ratchet_set import RatchetSet
import pytest

TEST_DB_PATH = "test_user.db"


def test_ratchet_set():
    # check if all getters and setters are running correctly. Sanity check
    rset = RatchetSet()
    ir_recv = InnerRatchet(token_bytes(SHARED_KEY_LENGTH))
    ir_send = InnerRatchet(token_bytes(SHARED_KEY_LENGTH))
    ir_root = InnerRatchet(token_bytes(SHARED_KEY_LENGTH))

    rset.recv_ratchet = ir_recv
    rset.send_ratchet = ir_send
    rset.root_ratchet = ir_root

    assert rset.recv_ratchet.get_snapshot() == ir_recv.get_snapshot()
    assert rset.send_ratchet.get_snapshot() == ir_send.get_snapshot()
    assert rset.root_ratchet.get_snapshot() == ir_root.get_snapshot()


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
        return_value=True,
    )

    test_ratchet_set = RatchetSet()
    inner_root = InnerRatchet(exp_shared_key)

    test_ratchet_set.root_ratchet = inner_root
    test_ratchet_set.send_ratchet = InnerRatchet(inner_root.turn()[0])
    test_ratchet_set.recv_ratchet = InnerRatchet(inner_root.turn()[0])

    mocker.patch(
        "app.database.db_controller.DatabaseController.load_ratchets",
        return_value=test_ratchet_set,
    )
    alice_clone_chat.init_ratchets()
    alice_clone_r_set = alice_clone_chat.get_ratchet_set()

    """Now we allow original alice to create her ratchets as she would
     normally do 
    """
    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False,  # Value here changes !!
    )
    mocker.patch(
        "app.database.db_controller.DatabaseController.get_chat_shared_key",
        return_value=exp_shared_key,  # Value here changes !!
    )
    alice_chat.init_ratchets()
    alice_r_set = alice_chat.get_ratchet_set()

    assert (
        alice_clone_r_set.root_ratchet.get_snapshot()
        == alice_r_set.root_ratchet.get_snapshot()
    )
    assert (
        alice_clone_r_set.send_ratchet.get_snapshot()
        == alice_r_set.send_ratchet.get_snapshot()
    )
    assert (
        alice_clone_r_set.recv_ratchet.get_snapshot()
        == alice_r_set.recv_ratchet.get_snapshot()
    )


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
    """
    Testing if the public keyes are properly generated
    and Diffie-Hellman is turning correctly
    """
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    alice = ChatMember(alice_state, "ewiqoeoiq", True)
    alice.initialize_symmertic_ratchets(exp_shared_key)

    bob = ChatMember(bob_state, "alicejksndka", False)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    """
    NOTE: Communication beetween two parties should
    never look like this !!!
    """
    alice.rotate_dh_ratchet(bob.get_dh_public_key())

    alice_r_set = alice.get_ratchet_set()
    bob_r_set = bob.get_ratchet_set()

    assert alice_r_set.recv_ratchet.get_snapshot() == bob_r_set.send_ratchet.get_snapshot()
    
    """ 
    We will perform now an illegal operation -> double turn of the dh_ratchet
    without any operation so we will supress this error for now.
    """
    bob.my_turn = True

    # to test this the other way we need to turn bob dh_ratchet
    bob.rotate_dh_ratchet(alice.get_dh_public_key())
    assert bob_r_set.recv_ratchet.turn() == alice_r_set.send_ratchet.turn()

    # assert bob_r_set.root_ratchet.get_snapshot() == alice_r_set.root_ratchet.get_snapshot()
    """
    NOTE: From the design the root_ratchet will always 
    be diffrent on the 2 sides of conversation
    """


def test_send_recieve_alice_first(mocker):
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    # I transaction: Initiator sets the send ratchet first
    alice = ChatMember(alice_state, "ewiqoeoiq", True)
    bob = ChatMember(bob_state, "alicejksndka", False)

    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False,
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController.get_chat_shared_key",
        return_value=exp_shared_key,
    )

    # II transaction: Second party sets their DH ratchets from shared key
    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    # III transaction: Initiator turns his dh_ratchet once 
    # to synchronise with the other party
    alice.rotate_dh_ratchet(bob.get_dh_public_key())

    # SENDING MESSAGE:
    """Alice sends the message first so she must ensure that the dh ratchet is turned
    """
    msg1 = "wysyłam messydź, ==+-()@#$ Żółśćśńź".encode(PREFFERED_ENCODING)
    msg3 = "elo elo 320 dsjandjksan".encode(PREFFERED_ENCODING)

    """
    NOTE: 
    Tldr: 
    So basicly rotations of the ratchets are perfomed as follows:
        - root_ratchet - turns on initialization, and per dh_ratchet rotation
        - send_ratchet - turns per send operation
        - recv_ratchet - turns per recieve operation
        - dh_ratchet - is derived from dh exchange and root_ratchet turn output
    """
    enc = alice.encrypt(msg1)
    msg2 = bob.decrypt(enc,public_key=alice.get_dh_public_key(), initial=True)

    assert msg1 == msg2

    enc = alice.encrypt(msg1)
    msg2 = bob.decrypt(enc)

    assert msg1 == msg2

    enc = bob.encrypt(msg3)
    msg4 = alice.decrypt(enc, public_key=bob.get_dh_public_key(), initial=True)

    assert msg3 == msg4


def test_send_recieve_alice_second(mocker):
    """
    The same test as the one above the diffrence is the order
    of initializing the conversation parties.
    Now the bob is initialized FIRST
    """
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    # DIFFRENCE IS THE SECOND ARGUMENT VALUE
    alice = ChatMember(alice_state, "ewiqoeoiq", False)
    bob = ChatMember(bob_state, "alicejksndka", True)

    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False,
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController.get_chat_shared_key",
        return_value=exp_shared_key,
    )

    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    msg1 = "wysyłam messydź, ==+-()@#$ Żółśćśńź".encode(PREFFERED_ENCODING)

    # Since bob is an intiator -> he has to turn his dh_ratchet
    bob.rotate_dh_ratchet(alice.get_dh_public_key())

    """
    NOTE: As you can see, we did not turn the bob dh_ratchet 
    before recieving the message from alice, thats because bob
    has already turned his ratchet and alice did not.
    
    The rotation of dh_ratchet is performed alternately
    beetween two parties. 
    And because the state of the dh_ratchet is very tightly
    linked with the root_ratchet we cannot do the dh_ratchet
    rotation in advance.
    """
    enc = alice.encrypt(msg1)
    msg2 = bob.decrypt(enc)

    assert msg1 == msg2


def test_should_desynchronize_when_bad_initiator(mocker):
    """
    The same test as the one above the diffrence is
    bad order of message initialization.
    The order in double ratchet algorithm
    matters, so in the result the message should
    be messed up
    """
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    # THE ONLY DIFFRENCE IS THE SECOND ARGUMENT VALUE
    alice = ChatMember(alice_state, "ewiqoeoiq", True)
    bob = ChatMember(bob_state, "alicejksndka", False)

    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False,
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController.get_chat_shared_key",
        return_value=exp_shared_key,
    )

    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)
    alice.rotate_dh_ratchet(bob.get_dh_public_key())

    msg1 = "ndsjkankdsak".encode(PREFFERED_ENCODING)
    enc = alice.encrypt(msg1)

    with pytest.raises(ChatMemberException):
        bob.decrypt(enc)
    
    alice.my_turn = True
    bob.my_turn = False
    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    # double synchonization -> should fail
    alice.rotate_dh_ratchet(bob.get_dh_public_key())
    with pytest.raises(ChatMemberException):
        alice.rotate_dh_ratchet(bob.get_dh_public_key())
