""" Tests related with creation of the chat beetween two users
You will find here tests related with the 4 Diffie-Hellman
handshake. 
You will not find here tests related with server connection
and server confirmation.
Also you will not find here tests related with encrypting the messages
themselves
"""
from app.chat.crypto import Establisher, Guest
from app.user_state import UserState

TEST_DB_PATH = "db_data_test/user.db"


def test_basic_creation():
    alice_state = UserState("alice", "passw")
    bob_state = UserState("bob", "bobPass")
    alice = Guest(alice_state)
    bob = Establisher(bob_state)


def test_assigned_starter_keys():
    """Integrity test: Alice wants to meet Bob
    in the app. In real world the end user can be
    alice or bob
    """
    # alice is guest to Bob conversation
    alice_state = UserState("alice", "passw")
    bob_state = UserState("bob", "bobPass")
    alice = Guest(alice_state)
    bob = Establisher(bob_state)

    alice_public_id_key = alice.get_public_id_key()
    alice_ephemeral_key = alice.get_public_ephemeral_key()
    alice_chosen_otk_index = 0  # ONLY MAKES SENSE WHILE TESTING !! THIS IS ABSTRACTED
    

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
    """integrity test: save and load up the connection"""
    alice_state = UserState("alice", "password")
    bob_state = UserState("bob", "password")
    alice = Guest(alice_state)
    bob = Establisher(bob_state)

    bob_public_id_key = bob.get_public_id_key()
    bob_signed_prekey = bob.get_public_signed_key()
    bob_one_time_key = bob.get_public_one_time_key()
    alice_chosen_otk_index = 0  # ONLY MAKES SENSE WHILE TESTING !! THIS IS ABSTRACTED

    alice_public_id_key = alice.get_public_id_key()
    alice_ephemeral_key = alice.get_public_ephemeral_key()

    assert alice.create_shared_key_X3DH(
        id_key=bob_public_id_key,
        signed_prekey=bob_signed_prekey,
        one_time_key=bob_one_time_key,
    )

    assert bob.create_shared_key_X3DH(
        id_key=alice_public_id_key, ephemeral_key=alice_ephemeral_key
    )
    bob.save()
    alice.save()

    bob_prim = Establisher(bob_state, load_from_db=True)
    alice_prim = Guest(alice_state, load_from_db=True)

    bobp_pId = bob_prim.get_public_id_key()
    bobp_sig = bob_prim.get_public_signed_key()
    bobp_ot = bob_prim.get_public_one_time_key()

    alicep_pId = alice_prim.get_public_id_key()
    alicep_eph = alice_prim.get_public_ephemeral_key()

    assert alice_prim.create_shared_key_X3DH(
        id_key=bobp_pId, signed_prekey=bobp_sig, one_time_key=bobp_ot
    )

    assert bob_prim.create_shared_key_X3DH(
        id_key=alicep_pId, ephemeral_key=alicep_eph
    )


def test_send_message_to_confirmed_contact():
    """Itegrity test:
    At this scenario Alice and Bob are confirmed and
    established correct connection
    We test sending simple message from alice to bob
    """
    assert False
