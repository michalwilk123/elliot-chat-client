from app.app_controller import AppController
from app.user.user_functions import resolve_user_state
from app.chat.crypto.crypto_utils import (
    create_b64_from_private_key,
    create_b64_from_public_key,
    create_private_key_from_b64,
    create_public_key_from_b64,
    create_shared_key_X3DH_establisher,
    create_shared_key_X3DH_guest,
    generate_DH,
    private_key_to_bytes,
    aead_encrypt,
    aead_decrypt,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from app.user.user_state import UserState
from app.config import MAX_ONE_TIME_KEYS, PREFFERED_ENCODING
import os
import pytest

TEST_DB_PATH = "test_user.db"


def test_b64_2_private_key_conversion():
    """parse random private key multiple times
    to check if any information is lost
    """
    dummy_key = X25519PrivateKey.generate()
    b64_dummy_key = create_b64_from_private_key(dummy_key)
    to_compare_key = create_private_key_from_b64(b64_dummy_key)
    assert private_key_to_bytes(dummy_key) == private_key_to_bytes(
        to_compare_key
    )
    assert b64_dummy_key == create_b64_from_private_key(to_compare_key)


def test_aead_encryption():
    test_text = "mn,XCZCXZ ąćźśęŁÓŃ↑↑↑↑".encode("utf-8")
    some_key = "ndkjanjkdnask".encode("utf-8")

    enc = aead_encrypt(some_key, test_text, pad=True)

    decrypted = aead_decrypt(some_key, enc, pad=True)
    assert test_text == decrypted


def test_diffie_hellman_exchange():
    key_0 = generate_DH()
    key_1 = generate_DH()

    secret_0 = key_0.exchange(key_1.public_key())
    secret_1 = key_0.exchange(key_1.public_key())
    assert secret_0 == secret_1


def test_assigned_starter_keys(mocker):
    """Scenrario: Alice wants to meet Bob
    in the app.

    Application performs a X3DH protocol to exchange
    shared initial secret
    """
    # alice has send to bob a friend request
    alice_state = UserState("alice")
    bob_state = UserState("bob")

    mocker.patch(
        "app.database.db_controller.DatabaseController.get_user_keys",
        return_value=(generate_DH(), generate_DH()),
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController", return_value=None
    )

    resolve_user_state(alice_state, TEST_DB_PATH)
    resolve_user_state(bob_state, TEST_DB_PATH)

    alice_ephemeral = generate_DH()
    bob_otk = generate_DH()

    if alice_state.id_key is None:
        assert False, "alice key not assigned ??"

    shared_secret_alice = create_shared_key_X3DH_guest(
        alice_state.id_key,
        alice_ephemeral,
        bob_state.id_key.public_key(),
        bob_state.signed_pre_key.public_key(),
        bob_otk.public_key(),
    )

    if bob_state.id_key is None or bob_state.signed_pre_key is None:
        assert False, "bob key not assigned ??"

    shared_secret_bob = create_shared_key_X3DH_establisher(
        bob_state.id_key,
        bob_state.signed_pre_key,
        bob_otk,
        alice_state.id_key.public_key(),
        alice_ephemeral.public_key(),
    )

    assert shared_secret_alice == shared_secret_bob


def mask_api_controller(
    mocker,
    bob_idk: X25519PublicKey,
    bob_spk: X25519PublicKey,
    bob_otk: X25519PublicKey,
    chosen_otk_idx:int
):
    async def mocked_con_check(contact):
        assert type(contact) == str, "contact must be a string!!"
        return True

    async def mocked_con_info(contact):
        assert type(contact) == str, "contact must be a string!!"
        return {
            "success": True,
            "user_data": {
                "login": "alice",
                "public_id_key": create_b64_from_public_key(bob_idk).decode(
                    PREFFERED_ENCODING
                ),
                "public_signed_pre_key": create_b64_from_public_key(
                    bob_spk
                ).decode(PREFFERED_ENCODING),
                "success": True,
            },
        }

    async def mocked_get_otk():
        return (
            create_b64_from_public_key(bob_otk).decode(PREFFERED_ENCODING),
            chosen_otk_idx,
        )

    mocker.patch(
        "app.api.api_controller.ApiController.check_contact",
        side_effect=mocked_con_check,
    )

    mocker.patch(
        "app.api.api_controller.ApiController.get_contact_info",
        side_effect=mocked_con_info,
    )

    mocker.patch(
        "app.api.api_controller.ApiController.get_random_one_time_key",
        side_effect=mocked_get_otk,
    )


@pytest.mark.asyncio
async def test_full_x3dh(mocker):
    """
    Scenario:
    Declare shared secret
    beetween two parties. This time the above
    operation is performed inside the app!!
    Again Alice is sending the friend request
    to Bob
    """

    # to make the test independent we
    # ensure that the database will be created
    # from scratch
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    ALICE_LOGIN = "alice"
    BOB_LOGIN = "bob"

    # mocking initial check for end server aliveness
    mocker.patch(
        "app.app_controller.AppController.resolve_startup",
        side_effect=lambda: ...,
    )

    # mocking initial hello message
    mocker.patch("app.cli.utilities.startup", side_effect=lambda: ...)

    # mocking prompt for the alice username
    mocker.patch(
        "app.cli.utilities.get_credentials", side_effect=lambda: ALICE_LOGIN
    )

    mocker.patch(
        "app.app_controller.AppController.spin_async_event_loop",
        side_effect=lambda: ...,
    )

    alice_app_controller = AppController(TEST_DB_PATH)
    alice_app_controller.start(start_session=False)

    mocker.patch(
        "app.cli.utilities.get_credentials", side_effect=lambda: BOB_LOGIN
    )

    bob_app_controller = AppController(TEST_DB_PATH)
    bob_app_controller.start(start_session=False)

    bob_state = bob_app_controller.user_state

    assert (
        bob_state.id_key is not None and bob_state.signed_pre_key is not None
    ), "Bob has not initialized his keys"
    bob_otk_keys = bob_app_controller.db_controller.get_user_otk(bob_state)

    async def mocked_server_registration():
        return None

    async def mocked_otk_init(init_model):
        assert (
            init_model["login"] == bob_state.login
        ), "Sending login is not the same"
        assert (
            init_model["signature"] == bob_state.signature
        ), "Wrong user signature"
        assert (
            init_model["num_of_keys"] == MAX_ONE_TIME_KEYS
        ), "Wrong user signature"
        assert set(init_model["one_time_public_keys"]) == set(
            bob_otk_keys
        ), "Controller fetched wrong otk keys from database"

    # mocking initial server registration
    mocker.patch(
        "app.api.api_controller.ApiController.estabish_self_to_server",
        side_effect=mocked_server_registration,
    )

    mocker.patch(
        "app.api.api_controller.ApiController.establish_initial_otk",
        side_effect=mocked_otk_init,
    )
    resolve_user_state(bob_app_controller.user_state, TEST_DB_PATH)
    resolve_user_state(alice_app_controller.user_state, TEST_DB_PATH)

    await bob_app_controller.api_controller.create_user()

    ALICE_OTK_INDEX = 2

    mask_api_controller(
        mocker,
        bob_state.id_key.public_key(),
        bob_state.signed_pre_key.public_key(),
        create_public_key_from_b64(
            bob_otk_keys[ALICE_OTK_INDEX]
        ),
        ALICE_OTK_INDEX
    )

    invite = {}

    async def mocked_friend_request(schema):
        assert set(schema.keys()) == {
            "my_login",
            "signature",
            "contact_login",
            "public_id_key",
            "public_ephemeral_key",
            "otk_index",
        }
        nonlocal invite
        invite = schema


    mocker.patch(
        "app.api.api_controller.ApiController.send_friend_request",
        side_effect=mocked_friend_request,
    )

    await alice_app_controller.add_contact(BOB_LOGIN)
    bob_app_controller.api_controller.approve_new_contact(invite)

    """
    Both sides of the conversation are using the same sqlite
    file. This is intended for test. The controller for the database
    is designed to handle such cases
    """

    alice_shared_secret, _ = (
        alice_app_controller.db_controller.load_chat_init_variables(
            alice_app_controller.user_state, BOB_LOGIN
        )
    )

    bob_shared_secret, _ = (
        bob_app_controller.db_controller.load_chat_init_variables(
            bob_state, ALICE_LOGIN
        )
    )
    print("klucz alicji: ", alice_shared_secret)
    print("klucz bogdana",  bob_shared_secret)

    # Finally we check if both shared secrets are equal
    assert alice_shared_secret == bob_shared_secret, "The end secrets are not equal!!!"

