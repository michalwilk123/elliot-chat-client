""" Tests related with creation of the chat beetween two users
You will find here tests related with the 3 Diffie-Hellman
handshake. 
You will not find here tests related with server connection
and server confirmation.
Also you will not find here tests related with encrypting the messages
themselves
"""
from app.chat.crypto import Establisher, Guest
from app.user_state import UserState
from app.database.db_controller import DatabaseController

TEST_DB_PATH = "db_data_test/user.db"


def test_basic_creation():
    alice_state = UserState("alice", "passw")
    bob_state = UserState("bob", "bobPass")
    alice = Guest(alice_state, DB_PATH=TEST_DB_PATH)
    bob = Establisher(bob_state, DB_PATH=TEST_DB_PATH)


def test_assigned_starter_keys():
    """Integrity test: Alice wants to meet Bob
    in the app. In real world the end user can be
    alice or bob
    """
    # alice is guest to Bob conversation
    alice_state = UserState("alice", "passw")
    bob_state = UserState("bob", "bobPass")
    alice = Guest(alice_state, DB_PATH=TEST_DB_PATH)
    bob = Establisher(bob_state, DB_PATH=TEST_DB_PATH)

    alice_public_id_key = alice.get_public_id_key()
    alice_ephemeral_key = alice.get_public_ephemeral_key()

    alice_chosen_otk_index = (
        0  # ONLY MAKES SENSE WHILE TESTING !! THIS IS ABSTRACTED
    )
    bob.set_one_time_key(alice_chosen_otk_index)

    bob_public_id_key = bob.get_public_id_key()
    bob_signed_prekey = bob.get_public_signed_key()
    bob_one_time_key = bob.get_public_one_time_key()

    # checking if guest executed 4 dh handsahke correctly
    alice.create_shared_key_X3DH(
        id_key=bob_public_id_key,
        signed_prekey=bob_signed_prekey,
        one_time_key=bob_one_time_key,
    )

    # checking if establisher has established connection correctly
    bob.create_shared_key_X3DH(
        id_key=alice_public_id_key, ephemeral_key=alice_ephemeral_key
    )

    alice_skey = alice.get_shared_key()
    bob_skey = bob.get_shared_key()

    # below operation should be made irl xdd
    assert alice_skey == bob_skey
    assert alice.shared_key == bob.shared_key


def test_initialize_session():
    """
    integrity test: save and load up the connection.
    This time using the database
    """
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")

    db_controller = DatabaseController(DB_PATH=TEST_DB_PATH)
    db_controller._reinstall()
    db_controller.create_user(alice_state)
    db_controller.create_user(bob_state)
    del db_controller

    alice = Guest(alice_state, DB_PATH=TEST_DB_PATH)
    bob = Establisher(bob_state, DB_PATH=TEST_DB_PATH)
    alice_chosen_otk_index = (
        0  # TODO: ONLY MAKES SENSE WHILE TESTING !! THIS IS ABSTRACTED
    )
    bob.set_one_time_key(alice_chosen_otk_index)

    bob_public_id_key = bob.get_public_id_key()
    bob_signed_prekey = bob.get_public_signed_key()
    bob_one_time_key = bob.get_public_one_time_key()

    alice_public_id_key = alice.get_public_id_key()
    alice_ephemeral_key = alice.get_public_ephemeral_key()

    alice.create_shared_key_X3DH(
        id_key=bob_public_id_key,
        signed_prekey=bob_signed_prekey,
        one_time_key=bob_one_time_key,
    )

    bob.create_shared_key_X3DH(
        id_key=alice_public_id_key, ephemeral_key=alice_ephemeral_key
    )
    bob.save()
    alice.save()

    bob_prim = Establisher(bob_state, load_from_db=True, DB_PATH=TEST_DB_PATH)
    alice_prim = Guest(alice_state, load_from_db=True, DB_PATH=TEST_DB_PATH)
    bob_prim.set_one_time_key(alice_chosen_otk_index)

    bobp_pId = bob_prim.get_public_id_key()
    bobp_sig = bob_prim.get_public_signed_key()
    bobp_ot = bob_prim.get_public_one_time_key()

    alicep_pId = alice_prim.get_public_id_key()
    alicep_eph = alice_prim.get_public_ephemeral_key()

    alice_prim.create_shared_key_X3DH(
        id_key=bobp_pId, signed_prekey=bobp_sig, one_time_key=bobp_ot
    )

    bob_prim.create_shared_key_X3DH(
        id_key=alicep_pId, ephemeral_key=alicep_eph
    )
    assert alice_prim.shared_key == bob_prim.shared_key


def test_initialize_ratchets():
    assert False


def test_create_contact_with_ratchets():
    assert False
