from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from app.database.db_controller import (
    DatabaseController,
    DatabaseControllerException,
)
from app.user_state import UserState
from app.chat.crypto.ratchet_set import RatchetSet
from app.chat.crypto.crypto_utils import create_b64_from_private_key
from app.chat.crypto.inner_ratchet import InnerRatchet
import pytest
import types
from secrets import token_bytes

TEST_DB_PATH = "test_user.db"


@pytest.fixture(autouse=True)
def db_init():
    """
    Reseting the database before every test.
    Also declaring new path for the controller to not override
    current data
    """
    args = types.SimpleNamespace()
    args.alice_state = UserState("Alice", "passw")
    args.db_controller = DatabaseController(DB_PATH=TEST_DB_PATH)
    args.db_controller._reinstall()

    args.db_controller.create_user(args.alice_state)
    return args


def test_should_throw_no_user(db_init):
    charlie_state = UserState("Charlie", "char_password")

    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.add_contact(charlie_state, "Carol")


def test_should_run_fine():
    DatabaseController(DB_PATH=TEST_DB_PATH)


def test_should_throw_contact_error(db_init):
    # thow exception when trying to add self to the contact list
    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.add_contact(db_init.alice_state, "Alice")


def test_create_user(db_init):
    lee_state = UserState("Lee", "lee_password")

    assert db_init.db_controller.user_exists(db_init.alice_state)
    assert not db_init.db_controller.user_exists(lee_state)


def test_delete_user(db_init):
    db_init.db_controller.delete_user(db_init.alice_state)
    assert not db_init.db_controller.user_exists(db_init.alice_state)


def test_should_throw_when_user_does_not_exists(db_init):
    lee_state = UserState("Lee", "lee_password")
    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.delete_user(lee_state)


def test_add_contact(db_init):
    db_init.db_controller.add_contact(db_init.alice_state, "Bob")

    assert db_init.db_controller.contact_exists(db_init.alice_state, "Bob")
    assert not db_init.db_controller.contact_exists(
        db_init.alice_state, "Oscar"
    )


def test_get_contacts(db_init):
    db_init.db_controller.add_contact(db_init.alice_state, "Bob")
    db_init.db_controller.add_contact(db_init.alice_state, "Charlie")
    db_init.db_controller.add_contact(db_init.alice_state, "Oscar")

    con_list = db_init.db_controller.get_user_contacts(db_init.alice_state)

    assert type(con_list) == list
    expected = {"Bob", "Charlie", "Oscar"}

    """We cannot control the sequence of incoming data
    Therefore we ignore it by treating it as set and applying
    union operation
    """
    con_list = set(con_list) | expected

    assert expected == con_list


def test_delete_contact(db_init):
    db_init.db_controller.add_contact(db_init.alice_state, "Charlie")
    db_init.db_controller.add_contact(db_init.alice_state, "Oscar")

    db_init.db_controller.delete_contact(db_init.alice_state, "Charlie")


def test_should_throw_when_contact_does_not_exists(db_init):
    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.delete_contact(db_init.alice_state, "Charlie")


def test_save_load_ratchets(db_init):
    test_contact = "Charlie"
    db_init.db_controller.add_contact(db_init.alice_state, test_contact)
    r_set = RatchetSet()

    r_set.root_ratchet = InnerRatchet(token_bytes(10))
    r_set.send_ratchet = InnerRatchet(token_bytes(10))
    r_set.recv_ratchet = InnerRatchet(token_bytes(10))
    r_set.dh_ratchet = X25519PrivateKey.generate()

    db_init.db_controller.save_ratchets(db_init.alice_state, test_contact, r_set)

    r_set_out:RatchetSet = db_init.db_controller.load_ratchets(db_init.alice_state, test_contact)

    assert r_set.root_ratchet.get_snapshot() == r_set_out.root_ratchet.get_snapshot()
    assert r_set.send_ratchet.get_snapshot() == r_set_out.send_ratchet.get_snapshot()
    assert r_set.recv_ratchet.get_snapshot() == r_set_out.recv_ratchet.get_snapshot()
    assert create_b64_from_private_key(r_set.dh_ratchet) == create_b64_from_private_key(r_set_out.dh_ratchet)

