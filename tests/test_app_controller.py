from app.config import PREFFERED_ENCODING
from app.api.api_controller import ApiController
from app.chat.crypto.crypto_utils import (
    create_b64_from_public_key,
    generate_DH,
)
from app.user.user_state import UserState
from app.app_controller import AppController, ContactNotFoundException
import pytest

TEST_DB_PATH = "test_user.db"


def init_mocker(mocker):
    async def mocked_con_check(contact):
        assert type(contact) == str, "contact must be a string!!"
        return True

    async def mocked_con_info(contact):
        assert type(contact) == str, "contact must be a string!!"
        return {
            "success": True,
            "user_data": {
                "login": "alice",
                "public_id_key": create_b64_from_public_key(
                    generate_DH().public_key()
                ).decode(PREFFERED_ENCODING),
                "public_signed_pre_key": create_b64_from_public_key(
                    generate_DH().public_key()
                ).decode(PREFFERED_ENCODING),
                "success": True,
            },
        }

    async def mocked_get_otk():
        return (
            create_b64_from_public_key(generate_DH().public_key()).decode(
                PREFFERED_ENCODING
            ),
            1,
        )

    async def mocked_friend_request(schema):
        assert set(schema.keys()) == {
            "my_login",
            "signature",
            "contact_login",
            "public_id_key",
            "public_ephemeral_key",
            "otk_index",
        }

    def mocked_x3dh(*args, **kwargs):
        assert not None in args, "not initialized key passed for exchange!!"
        assert (
            not None in kwargs.values()
        ), "not initialized key passed for exchange!!"
        assert len(args) + len(kwargs) == 5

    def mocked_db_add_contact(*args, **kwargs):
        assert not None in args, "not initialized key passed for exchange!!"
        assert (
            not None in kwargs.values()
        ), "not initialized key passed for exchange!!"
        assert len(args) + len(kwargs) == 7

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

    mocker.patch(
        "app.api.api_controller.ApiController.send_friend_request",
        side_effect=mocked_friend_request,
    )

    mocker.patch(
        "app.chat.crypto.crypto_utils.create_shared_key_X3DH_guest",
        side_effect=mocked_x3dh,
    )

    mocker.patch(
        "app.database.db_controller.DatabaseController.add_contact",
        side_effect=mocked_db_add_contact,
    )


@pytest.fixture
def app_cont_prep(mocker):
    mocker.patch(
        "app.app_controller.AppController.resolve_startup",
        side_effect=lambda: ...,
    )
    state = UserState("alice")
    state.id_key = generate_DH()
    state.signed_pre_key = generate_DH()

    app_controller = AppController(db_path=TEST_DB_PATH)
    app_controller.user_state = state
    app_controller.api_controller = ApiController(
        state,
        app_controller.db_controller,
        init_session=False,
        register_user=False,
    )
    return app_controller


@pytest.mark.asyncio
async def test_add_contact(mocker, app_cont_prep):
    """
    Normal use of the add_contact function without any errors
    """
    init_mocker(mocker)
    await app_cont_prep.add_contact("bob")


@pytest.mark.asyncio
async def test_should_raise_when_friend_not_registered(mocker, app_cont_prep):
    init_mocker(mocker)

    async def mocked_con_info(contact):
        return {"success": False, "user_data": None}

    mocker.patch(
        "app.api.api_controller.ApiController.get_contact_info",
        side_effect=mocked_con_info,
    )

    with pytest.raises(ContactNotFoundException):
        await app_cont_prep.add_contact("bob")
