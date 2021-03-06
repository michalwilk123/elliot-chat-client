from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from app.database.db_controller import (
    ContactParametersError,
    DatabaseController,
    DatabaseControllerException,
)
from app.user.user_state import UserState
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
    args.alice_state = UserState("Alice")
    args.db_controller = DatabaseController(DB_PATH=TEST_DB_PATH)
    args.db_controller._reinstall()

    # raondom b64 strings representing keys
    args.b64_id = "3+IWTHCIArgvY+WLWXSk6w=="
    args.b64_shared = "LiF1F733QbLg1fMBjCmerQ=="
    args.con_spk = "NauGyCz9V2QYyfIJ9x4XwQ=="
    args.con_ephem = "cWpmLwqk5+/5ZPiD7FOnjw=="
    args.my_ephem = "F2GQ8SMSm21jMyDrS6Y"
    args.con_otk = "HjKlZZDAM1p7Gn6KhPw"
    args.my_otk = "11CYXDhP3n3ND9S1nLk"

    args.db_controller.create_user(args.alice_state)
    return args


def test_should_throw_no_user_added(db_init):
    """
    We are trying to add new contact to user
    which is not registered to the database
    """
    charlie_state = UserState("Charlie")

    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.add_contact(
            charlie_state,
            "Carol",
            db_init.b64_id,
            db_init.b64_shared,
            contact_signed_pre_key=db_init.con_spk,
            my_ephemeral_key=db_init.my_ephem,
            contact_otk_key=db_init.con_otk,
        )


def test_should_throw_data_not_complete(db_init):

    with pytest.raises(ContactParametersError):
        db_init.db_controller.add_contact(
            db_init.alice_state,
            "Charlie",
            db_init.b64_id,
            db_init.b64_shared,
            my_ephemeral_key=db_init.my_ephem,
            contact_ephemeral_key=db_init.con_ephem,
            contact_otk_key=db_init.con_otk,
        )


def test_should_run_fine():
    DatabaseController(DB_PATH=TEST_DB_PATH)


def test_should_throw_contact_error(db_init):
    # thow exception when trying to add self to the contact list
    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.add_contact(
            db_init.alice_state,
            "Alice",
            db_init.b64_id,
            db_init.b64_shared,
            contact_signed_pre_key=db_init.con_spk,
            my_ephemeral_key=db_init.my_ephem,
            contact_otk_key=db_init.con_otk,
        )


def test_create_contact_guest(db_init):
    assert db_init.db_controller.add_contact(
        db_init.alice_state,
        "Bob",
        db_init.b64_id,
        db_init.b64_shared,
        contact_signed_pre_key=db_init.con_spk,
        my_ephemeral_key=db_init.my_ephem,
        contact_otk_key=db_init.con_otk,
    )


def test_create_contact_estab(db_init):
    assert db_init.db_controller.add_contact(
        db_init.alice_state,
        "Bob",
        db_init.b64_id,
        db_init.b64_shared,
        contact_ephemeral_key=db_init.con_ephem,
        my_otk_key=db_init.con_otk,
    )


def test_should_return_false_when_contact_exist(db_init):
    assert db_init.db_controller.add_contact(
        db_init.alice_state,
        "Bob",
        db_init.b64_id,
        db_init.b64_shared,
        contact_ephemeral_key=db_init.con_ephem,
        my_otk_key=db_init.con_otk,
    )

    assert not db_init.db_controller.add_contact(
        db_init.alice_state,
        "Bob",
        db_init.b64_id,
        db_init.b64_shared,
        contact_ephemeral_key=db_init.con_ephem,
        my_otk_key=db_init.con_otk,
    )


def test_create_user(db_init):
    lee_state = UserState("Lee")

    assert db_init.db_controller.user_exists(db_init.alice_state)
    assert not db_init.db_controller.user_exists(lee_state)


def test_delete_user(db_init):
    assert db_init.db_controller.user_exists(db_init.alice_state)
    db_init.db_controller.delete_user(db_init.alice_state)
    assert not db_init.db_controller.user_exists(db_init.alice_state)


def test_should_throw_when_user_does_not_exists(db_init):
    lee_state = UserState("Lee")
    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.delete_user(lee_state)


def test_get_contacts(db_init):
    args = db_init.b64_id, db_init.b64_shared
    kwargs = {
        "contact_ephemeral_key": db_init.con_ephem,
        "my_otk_key": db_init.con_otk,
    }

    db_init.db_controller.add_contact(
        db_init.alice_state, "Bob", *args, **kwargs
    )
    db_init.db_controller.add_contact(
        db_init.alice_state, "Charlie", *args, **kwargs
    )
    db_init.db_controller.add_contact(
        db_init.alice_state, "Oscar", *args, **kwargs
    )

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
    args = db_init.b64_id, db_init.b64_shared
    kwargs = {
        "contact_ephemeral_key": db_init.con_ephem,
        "my_otk_key": db_init.con_otk,
    }
    db_init.db_controller.add_contact(
        db_init.alice_state, "Charlie", *args, **kwargs
    )
    db_init.db_controller.add_contact(
        db_init.alice_state, "Oscar", *args, **kwargs
    )

    db_init.db_controller.delete_contact(db_init.alice_state, "Charlie")


def test_should_throw_when_deleted_contact_does_not_exists(db_init):
    with pytest.raises(DatabaseControllerException):
        db_init.db_controller.delete_contact(db_init.alice_state, "Charlie")


def test_save_load_ratchets(db_init):
    args = db_init.b64_id, db_init.b64_shared
    kwargs = {
        "contact_ephemeral_key": db_init.con_ephem,
        "my_otk_key": db_init.con_otk,
    }
    test_contact = "Charlie"
    db_init.db_controller.add_contact(
        db_init.alice_state, test_contact, *args, **kwargs
    )

    r_set = RatchetSet()
    r_set.root_ratchet = InnerRatchet(token_bytes(10))
    r_set.send_ratchet = InnerRatchet(token_bytes(10))
    r_set.recv_ratchet = InnerRatchet(token_bytes(10))
    r_set.dh_ratchet = X25519PrivateKey.generate()

    db_init.db_controller.save_ratchets(
        db_init.alice_state, test_contact, r_set, True
    )

    r_set_out: RatchetSet = db_init.db_controller.load_ratchets(
        db_init.alice_state, test_contact
    )

    assert (
        r_set.root_ratchet.get_snapshot()
        == r_set_out.root_ratchet.get_snapshot()
    )
    assert (
        r_set.send_ratchet.get_snapshot()
        == r_set_out.send_ratchet.get_snapshot()
    )
    assert (
        r_set.recv_ratchet.get_snapshot()
        == r_set_out.recv_ratchet.get_snapshot()
    )
    assert create_b64_from_private_key(
        r_set.dh_ratchet
    ) == create_b64_from_private_key(r_set_out.dh_ratchet)


def test_save_load_init_vars(db_init):
    test_contact = "Charlie"
    args = db_init.b64_id, db_init.b64_shared
    kwargs = {
        "contact_signed_pre_key": db_init.con_spk,
        "my_ephemeral_key": db_init.my_ephem,
        "contact_otk_key": db_init.con_otk,
    }
    db_init.db_controller.add_contact(
        db_init.alice_state, test_contact, *args, **kwargs
    )

    test_turn = True
    test_shared = token_bytes(10)

    db_init.db_controller.save_chat_init_variables(
        db_init.alice_state, test_contact, test_shared, test_turn
    )

    shared_out, turn_out = db_init.db_controller.load_chat_init_variables(
        db_init.alice_state, test_contact
    )

    assert shared_out == test_shared
    assert test_turn == turn_out


def test_ratchets_present(db_init):
    test_contact = "Charlie"
    args = db_init.b64_id, db_init.b64_shared
    kwargs = {
        "contact_signed_pre_key": db_init.con_spk,
        "my_ephemeral_key": db_init.my_ephem,
        "contact_otk_key": db_init.con_otk,
    }
    db_init.db_controller.add_contact(
        db_init.alice_state, test_contact, *args, **kwargs
    )

    r_set = RatchetSet()
    r_set.root_ratchet = InnerRatchet(token_bytes(10))
    r_set.send_ratchet = InnerRatchet(token_bytes(10))
    r_set.recv_ratchet = InnerRatchet(token_bytes(10))
    r_set.dh_ratchet = X25519PrivateKey.generate()

    assert not db_init.db_controller.ratchets_present(
        db_init.alice_state, test_contact
    )

    r_set.recv_ratchet = InnerRatchet(token_bytes(10))
    db_init.db_controller.save_ratchets(
        db_init.alice_state, test_contact, r_set, True
    )
    assert db_init.db_controller.ratchets_present(
        db_init.alice_state, test_contact
    )
