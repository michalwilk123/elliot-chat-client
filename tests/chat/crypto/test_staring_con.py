from app.chat.crypto import Establisher, Guest, establisher
from app.user_state import UserState

TEST_DB_PATH = "db_data_test/user.db"

def test_assigned_starter_keys():
    """Integrity test: Alice wants to meet Bob 
    in the app. In real world the end user can be 
    alice or bob
    """
    # alice is guest to Bob conversation
    alice = Guest()
    bob = Establisher()

    bob_public_id_key = bob.get_public_id_key()
    bob_signed_prekey = bob.get_public_signed_key()
    bob_one_time_key = bob.get_public_one_time_key()

    alice_public_id_key = alice.get_public_id_key()
    alice_ephemeral_key = alice.get_public_ephemeral_key()

    # checking if guest executed 4 dh handsahke correctly
    assert alice.confirm(
        id_key=bob_public_id_key
        signed_prekey=bob_signed_prekey,
        one_time_key=bob_one_time_key)

    # checking if establisher has established connection correctly
    assert bob.confirm(
        guest_id_key=alice_public_id_key,
        guest_ephemeral_key=alice_ephemeral_key
    )


def test_initialize_session():
    """integrity test: save and load up the connection
    """
    alice_state = UserState("alice", "password")
    alice = Guest()
    bob = Establisher()

    bob_public_id_key = bob.get_public_id_key()
    bob_signed_prekey = bob.get_public_signed_key()
    bob_one_time_key = bob.get_random_public_one_time_key()

    alice_public_id_key = alice.get_public_id_key()
    alice_ephemeral_key = alice.get_public_ephemeral_key()

    assert alice.confirm(
        id_key=bob_public_id_key
        signed_prekey=bob_signed_prekey,
        one_time_key=bob_one_time_key
    )

    assert bob.confirm(
        guest_id_key=alice_public_id_key,
        guest_ephemeral_key=alice_ephemeral_key
    )
    bob.save()
    alice.save()

    bob_prim = Establisher(load_from_db=True)
    alice_prim = Guest(load_from_db=True)

    bobp_pId = bob_prim.get_public_id_key()
    bobp_sig = bob_prim.get_public_signed_key()
    bobp_ot = bob_prim.get_random_public_one_time_key()

    alicep_pId = alice_prim.get_public_id_key()
    alicep_eph = alice_prim.get_public_ephemeral_key()

    assert alice_prim.confirm(
        id_key=bobp_pId,
        signed_prekey=bobp_sig,
        one_time_key=bobp_ot
    )

    assert bob_prim.confirm(
        guest_id_key=alicep_pId,
        guest_ephemeral_key=alicep_pId
    )


def test_send_message_to_confirmed_contact():
    """Itegrity test:
    At this scenario Alice and Bob are confirmed and 
    established correct connection
    We test sending simple message from alice to bob
    """