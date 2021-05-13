from app.user.user_state import UserState
from secrets import token_bytes
from app.config import PREFFERED_ENCODING, SHARED_KEY_LENGTH
from app.chat.crypto.inner_ratchet import InnerRatchet
from app.chat.crypto_controller import (
    CryptoController,
    CryptoControllerException,
)
from app.chat.crypto.ratchet_set import RatchetSet
import pytest
import os
from app.chat.crypto.crypto_utils import (
    create_b64_from_private_key,
    create_b64_from_public_key,
    create_shared_key_X3DH_establisher,
    create_shared_key_X3DH_guest,
    generate_DH,
)
from app.user.user_functions import resolve_user_state
from app.database.db_controller import DatabaseController
import binascii

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
    alice_state = UserState("alice")
    alice_clone_state = UserState("alice_clone")

    alice_chat = CryptoController(alice_state, "dsnkjdsnak", True)
    alice_clone_chat = CryptoController(alice_clone_state, "cnxzcxzbcmz", True)
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    """
    Fabrication of the alice clone ratchets.
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
        "app.database.db_controller.DatabaseController"
        ".load_chat_init_variables",
        return_value=(exp_shared_key, True),  # Value here changes !!
    )
    mocker.patch(
        "app.database.db_controller.DatabaseController.save_ratchets",
        return_value=...,
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
    alice_state = UserState("alice")
    bob_state = UserState("bob")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    alice = CryptoController(alice_state, "ewiqoeoiq", True)
    bob = CryptoController(bob_state, "alicejksndka", False)

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
    alice_state = UserState("alice")
    bob_state = UserState("bob")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    alice = CryptoController(alice_state, "ewiqoeoiq", True)
    alice.initialize_symmertic_ratchets(exp_shared_key)

    bob = CryptoController(bob_state, "alicejksndka", False)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    """
    NOTE: Communication beetween two parties should
    never look like this !!!
    """
    alice.rotate_dh_ratchet(bob.get_dh_public_key())

    alice_r_set = alice.get_ratchet_set()
    bob_r_set = bob.get_ratchet_set()

    assert (
        alice_r_set.recv_ratchet.get_snapshot()
        == bob_r_set.send_ratchet.get_snapshot()
    )

    """
    We will perform now an illegal operation -> double turn of the dh_ratchet
    without any operation so we will supress this error for now.
    """
    bob.my_turn = True

    # to test this the other way we need to turn bob dh_ratchet
    bob.rotate_dh_ratchet(alice.get_dh_public_key())
    assert bob_r_set.recv_ratchet.turn() == alice_r_set.send_ratchet.turn()


def test_send_recieve_alice_first(mocker):
    alice_state = UserState("alice")
    bob_state = UserState("bob")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    # I transaction: Initiator sets the send ratchet first
    alice = CryptoController(alice_state, "ewiqoeoiq", True)
    bob = CryptoController(bob_state, "alicejksndka", False)

    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False,
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController"
        ".load_chat_init_variables",
        return_value=(exp_shared_key, True),
    )

    # II transaction: Second party sets their DH ratchets from shared key
    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    # III transaction: Initiator turns his dh_ratchet once
    # to synchronise with the other party
    alice.rotate_dh_ratchet(bob.get_dh_public_key())

    # SENDING MESSAGE:
    """
    Alice sends the message first so she must ensure that
    the dh ratchet is turned
    """
    msg1 = "L’homme est condamné à être libre".encode(PREFFERED_ENCODING)
    msg3 = "Je visite un point de pharmacie".encode(PREFFERED_ENCODING)

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
    msg2 = bob.decrypt(enc, public_key=alice.get_dh_public_key())

    assert msg1 == msg2

    enc = alice.encrypt(msg1)
    msg2 = bob.decrypt(enc)

    assert msg1 == msg2

    enc = bob.encrypt(msg3)
    msg4 = alice.decrypt(enc, public_key=bob.get_dh_public_key())

    assert msg3 == msg4


def test_send_recieve_alice_second(mocker):
    """
    The same test as the one above the diffrence is the order
    of initializing the conversation parties.
    Now the bob is initialized FIRST
    """
    alice_state = UserState("alice")
    bob_state = UserState("bob")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    # DIFFRENCE IS THE SECOND ARGUMENT VALUE
    alice = CryptoController(alice_state, "ewiqoeoiq", False)
    bob = CryptoController(bob_state, "alicejksndka", True)

    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False,
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController"
        ".load_chat_init_variables",
        return_value=(exp_shared_key, True),
    )

    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    msg1 = "wysyłam messydź, ==+-()@#$ Żółśćśńź".encode(PREFFERED_ENCODING)

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
    alice_state = UserState("alice")
    bob_state = UserState("bob")
    exp_shared_key = token_bytes(SHARED_KEY_LENGTH)

    # THE ONLY DIFFRENCE IS THE SECOND ARGUMENT VALUE
    alice = CryptoController(alice_state, "ewiqoeoiq", True)
    bob = CryptoController(bob_state, "alicejksndka", False)

    mocker.patch(
        "app.database.db_controller.DatabaseController.ratchets_present",
        return_value=False,
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController."
        "load_chat_init_variables",
        return_value=(exp_shared_key, True),
    )

    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)
    alice.rotate_dh_ratchet(bob.get_dh_public_key())

    msg1 = "ndsjkankdsak".encode(PREFFERED_ENCODING)
    enc = alice.encrypt(msg1)

    with pytest.raises(CryptoControllerException):
        bob.decrypt(enc)

    alice.my_turn = True
    bob.my_turn = False
    alice.initialize_symmertic_ratchets(exp_shared_key)
    bob.initialize_symmertic_ratchets(exp_shared_key)

    # double synchonization -> should fail
    alice.rotate_dh_ratchet(bob.get_dh_public_key())
    with pytest.raises(CryptoControllerException):
        alice.rotate_dh_ratchet(bob.get_dh_public_key())


def test_x3dh_double_ratchet_integration(mocker):
    """
    We perform the same operation as above but now
    the shared key is genereted by the application
    and database controller is not mocked this time
    """
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    ALICE_LOGIN = "alice"
    BOB_LOGIN = "bob"

    alice_state = UserState(ALICE_LOGIN)
    bob_state = UserState(BOB_LOGIN)

    db_controller = DatabaseController(TEST_DB_PATH)
    db_controller.create_user(alice_state)
    db_controller.create_user(bob_state)

    alice_emphem = generate_DH()
    bob_otk = generate_DH()

    assert alice_state.id_key is not None, "Alice priv key is not set!"
    assert bob_state.signed_pre_key is not None, "Bob spk key is not set!"
    assert bob_state.id_key is not None, "Bob priv key is not set!"

    shared_alice_secret = create_shared_key_X3DH_guest(
        alice_state.id_key,
        alice_emphem,
        bob_state.id_key.public_key(),
        bob_state.signed_pre_key.public_key(),
        bob_otk.public_key(),
    )

    shared_bob_secret = create_shared_key_X3DH_establisher(
        bob_state.id_key,
        bob_state.signed_pre_key,
        bob_otk,
        alice_state.id_key.public_key(),
        alice_emphem.public_key(),
    )

    # sanity check
    assert shared_alice_secret == shared_bob_secret, "keys must be equal!!"

    db_controller.add_contact(
        alice_state,
        BOB_LOGIN,
        create_b64_from_public_key(bob_state.id_key.public_key()).decode(
            PREFFERED_ENCODING
        ),
        binascii.b2a_base64(shared_alice_secret).decode(PREFFERED_ENCODING),
        contact_signed_pre_key=create_b64_from_public_key(
            bob_state.signed_pre_key.public_key()
        ).decode(PREFFERED_ENCODING),
        my_ephemeral_key=create_b64_from_private_key(alice_emphem).decode(
            PREFFERED_ENCODING
        ),
        contact_otk_key=create_b64_from_public_key(
            bob_otk.public_key()
        ).decode(PREFFERED_ENCODING),
    )

    db_controller.add_contact(
        bob_state,
        ALICE_LOGIN,
        create_b64_from_public_key(alice_state.id_key.public_key()).decode(
            PREFFERED_ENCODING
        ),
        binascii.b2a_base64(shared_bob_secret).decode(PREFFERED_ENCODING),
        contact_ephemeral_key=create_b64_from_public_key(
            alice_emphem.public_key()
        ).decode(PREFFERED_ENCODING),
        my_otk_key=create_b64_from_private_key(bob_otk).decode(
            PREFFERED_ENCODING
        ),
    )

    """
    NOTE: We did not defined who's turn it is. Thats because
    such information should be retrieved from the database!!!
    """
    alice_crypto_con = CryptoController(
        alice_state, BOB_LOGIN, DB_PATH=TEST_DB_PATH
    )
    bob_crypto_con = CryptoController(
        bob_state, ALICE_LOGIN, DB_PATH=TEST_DB_PATH
    )

    alice_crypto_con.init_ratchets(
        opt_public_key=bob_state.signed_pre_key.public_key()
    )
    bob_crypto_con.init_ratchets(opt_private_key=bob_state.signed_pre_key)

    # more sanity checks
    assert alice_crypto_con.my_turn is False, "This values should change!!!"
    assert bob_crypto_con.my_turn is True, "This value should change"

    alice_msg = "L’homme est condamné à être libre."
    message_for_bob = alice_crypto_con.encrypt_to_json_message(alice_msg)
    digested_msg = bob_crypto_con.decrypt_json_message(message_for_bob)

    alice_msg = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    message_for_bob = alice_crypto_con.encrypt_to_json_message(alice_msg)
    digested_msg = bob_crypto_con.decrypt_json_message(message_for_bob)

    # if this passes then ratchets are not moving preemptively
    assert alice_msg == digested_msg, "Second message failed to send"

    # Now Bob responds to alice
    bob_message = "k bro"
    message_for_alice = bob_crypto_con.encrypt_to_json_message(bob_message)
    digested_msg = alice_crypto_con.decrypt_json_message(message_for_alice)

    # if this passes then ratchets are not moving when they should
    assert bob_message == digested_msg, "Response failed to decrypt"


@pytest.mark.asyncio
async def test_continue_conversation():
    """
    Scenario: Alice had send to Bob friend request
    Both parties performed x3dh and are possessing shared secret.

    Now Alice sends to bob message and intializes
    conversation inside the application
    """
    shared_key = b"some secret key"

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    db_controller = DatabaseController(DB_PATH=TEST_DB_PATH)
    ALICE_LOGIN = "alice"
    BOB_LOGIN = "bob"

    alice_state = UserState(ALICE_LOGIN)
    bob_state = UserState(BOB_LOGIN)

    db_controller.create_user(alice_state)
    db_controller.create_user(bob_state)

    resolve_user_state(alice_state, TEST_DB_PATH)
    resolve_user_state(bob_state, TEST_DB_PATH)

    alice_ephem = generate_DH()
    bob_otk = generate_DH()

    alice_cryp = CryptoController(alice_state, BOB_LOGIN, DB_PATH=TEST_DB_PATH)
    bob_cryp = CryptoController(bob_state, ALICE_LOGIN, DB_PATH=TEST_DB_PATH)

    db_controller.add_contact(
        alice_state,
        BOB_LOGIN,
        create_b64_from_public_key(bob_state.id_key.public_key()).decode(
            PREFFERED_ENCODING
        ),
        binascii.b2a_base64(shared_key).decode(PREFFERED_ENCODING),
        contact_signed_pre_key=create_b64_from_public_key(
            bob_state.signed_pre_key.public_key()
        ).decode(PREFFERED_ENCODING),
        my_ephemeral_key=create_b64_from_private_key(alice_ephem).decode(
            PREFFERED_ENCODING
        ),
        contact_otk_key=create_b64_from_public_key(
            bob_otk.public_key()
        ).decode(PREFFERED_ENCODING),
    )

    db_controller.add_contact(
        bob_state,
        ALICE_LOGIN,
        create_b64_from_public_key(alice_state.id_key.public_key()).decode(
            PREFFERED_ENCODING
        ),
        binascii.b2a_base64(shared_key).decode(PREFFERED_ENCODING),
        contact_ephemeral_key=create_b64_from_public_key(
            alice_ephem.public_key()
        ).decode(PREFFERED_ENCODING),
        my_otk_key=create_b64_from_private_key(bob_otk).decode(
            PREFFERED_ENCODING
        ),
    )

    alice_cryp.init_ratchets(
        opt_public_key=bob_state.signed_pre_key.public_key()
    )
    bob_cryp.init_ratchets(opt_private_key=bob_state.signed_pre_key)

    old_alice_rset = alice_cryp.get_ratchet_set()
    old_bob_rset = bob_cryp.get_ratchet_set()

    # we delete last session
    del alice_cryp
    del bob_cryp
    del alice_state
    del bob_state

    alice_state = UserState(ALICE_LOGIN)
    bob_state = UserState(BOB_LOGIN)

    resolve_user_state(alice_state, TEST_DB_PATH)
    resolve_user_state(bob_state, TEST_DB_PATH)

    alice_cryp = CryptoController(alice_state, BOB_LOGIN, DB_PATH=TEST_DB_PATH)
    bob_cryp = CryptoController(bob_state, ALICE_LOGIN, DB_PATH=TEST_DB_PATH)

    # sanity checks
    assert db_controller.ratchets_present(
        alice_state, BOB_LOGIN
    ), "alice ratchets not established"
    assert db_controller.ratchets_present(
        bob_state, ALICE_LOGIN
    ), "bob ratchets not established"

    with pytest.raises(AssertionError):
        alice_cryp.init_ratchets(
            opt_public_key=bob_state.signed_pre_key.public_key()
        )

    with pytest.raises(AssertionError):
        bob_cryp.init_ratchets(opt_private_key=bob_state.signed_pre_key)

    alice_cryp.init_ratchets()
    bob_cryp.init_ratchets()

    new_alice_rset = alice_cryp.get_ratchet_set()
    new_bob_rset = bob_cryp.get_ratchet_set()

    # we now check if ratchet sets are equal
    assert (
        new_alice_rset.recv_ratchet.get_snapshot()
        == old_alice_rset.recv_ratchet.get_snapshot()
    )
    assert (
        new_alice_rset.root_ratchet.get_snapshot()
        == old_alice_rset.root_ratchet.get_snapshot()
    )
    assert (
        new_alice_rset.send_ratchet.get_snapshot()
        == old_alice_rset.send_ratchet.get_snapshot()
    )

    assert (
        new_bob_rset.recv_ratchet.get_snapshot()
        == old_bob_rset.recv_ratchet.get_snapshot()
    )
    assert (
        new_bob_rset.root_ratchet.get_snapshot()
        == old_bob_rset.root_ratchet.get_snapshot()
    )
    assert (
        new_bob_rset.send_ratchet.get_snapshot()
        == old_bob_rset.send_ratchet.get_snapshot()
    )

    assert alice_cryp.my_turn is False, "This values should change!!!"
    assert bob_cryp.my_turn is True, "This value should change"

    # -- now everything should be ready for conversation ---

    alice_msg = (
        "According to all known laws of aviation"
        ", there is no way a bee should be able to fly."
    )

    enc_msg = alice_cryp.encrypt_to_json_message(alice_msg)
    digested = bob_cryp.decrypt_json_message(enc_msg)

    assert alice_msg == digested, "Messages not encrypted correctly"

    bob_msg = (
        "Its wings are too small to get" "its fat little body off the ground."
    )

    enc_msg = bob_cryp.encrypt_to_json_message(bob_msg)
    digested = alice_cryp.decrypt_json_message(enc_msg)

    assert bob_msg == digested, "Messages not encrypted correctly"

    bob_msg = (
        "The bee, of course, flies anyway"
        "because bees don't care"
        "what humans think is impossible."
    )

    enc_msg = bob_cryp.encrypt_to_json_message(bob_msg)
    digested = alice_cryp.decrypt_json_message(enc_msg)

    assert bob_msg == digested, "Messages not encrypted correctly"
