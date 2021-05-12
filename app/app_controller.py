import binascii
from typing import Optional

from app.chat.crypto.crypto_utils import (
    create_b64_from_private_key,
    create_b64_from_public_key,
    create_public_key_from_b64,
    generate_DH,
    create_shared_key_X3DH_guest,
)
from .api.api_controller import ApiController
from .user.user_state import UserState
from .cli import utilities, chat
from .config import (
    DEFAULT_DB_PATH,
    MainMenuOptions,
    PREFFERED_ENCODING,
    SERVER_URL,
)
from .database.db_controller import DatabaseController
from .chat.chat_controller import ChatController
import asyncio
import urllib.request
from colorama import init, deinit
import urllib.error
from .routes import ApiRoutes


class AppControllerException(Exception):
    ...


class ContactNotFoundException(Exception):
    ...


class NotOneTimeKeysLeft(Exception):
    ...


class AppController:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self._url = SERVER_URL
        self.resolve_startup()
        self.db_controller = DatabaseController(DB_PATH=db_path)
        self._db_path = db_path

    def choose_reciever(self) -> Optional[str]:
        """choosing contact to have chat with
        Returns:
            str: chosen contact login
        """
        contacts = self.db_controller.get_user_contacts(self.user_state)
        contacts.append("Back")
        chosen = chat.choose_contact(contacts)
        if chosen == len(contacts) - 1:
            return None
        return contacts[chosen]

    def resolve_startup(self):
        try:
            resp = urllib.request.urlopen(self._url + ApiRoutes.ALIVE)
            resp.close()
            pass
        except urllib.error.URLError:
            print(f"Cannot connect to the server URL: {self._url}")

        init(autoreset=True)

    def spin_async_event_loop(self):
        loop = asyncio.get_event_loop()
        serv_task = loop.create_task(self.api_controller.server_task())
        loop.run_until_complete(self.main_menu())
        serv_task.cancel()

    def start(self, start_session: bool = True):
        utilities.startup()
        login = utilities.get_credentials()

        self.user_state = UserState(login)
        user_exist = self.db_controller.user_exists(self.user_state)

        if not user_exist:
            self.db_controller.create_user(self.user_state)
        else:
            id_key, sg_key = self.db_controller.get_user_keys(self.user_state)
            self.user_state.id_key = id_key
            self.user_state.signed_pre_key = sg_key

        # resolve_user_state(self.user_state, self._db_path)

        self.api_controller = ApiController(
            self.user_state,
            self.db_controller,
            register_user=not user_exist,
            init_session=start_session,
        )

        self.spin_async_event_loop()

    async def main_menu(self):
        while True:
            option = utilities.get_menu_option()

            if option == MainMenuOptions.MESSAGE:
                reciever = self.choose_reciever()
                if reciever is None:
                    continue
                self.__chat_controller = ChatController(
                    self.api_controller, reciever
                )

                self.__chat_controller.start()
                del self.__chat_controller
            elif option == MainMenuOptions.ADD_FRIEND:
                contact_name = await utilities.get_contact_name()
                await self.add_contact(contact_name)
            elif option == MainMenuOptions.CHANGE_CREDENTIALS:
                print("not implemented")
            elif option == MainMenuOptions.REMOVE_ACCOUNT:
                print("not implemented")
            elif option == MainMenuOptions.WAITROOM:
                await self.init_waitroom()
            elif option == MainMenuOptions.EXIT:
                print("bye")
                break
            else:
                raise RuntimeError("This option currently is not implemented")
        print("cleanup")
        await self.api_controller.client_session.close()
        deinit()

    async def init_waitroom(self):
        ...

    async def add_contact(self, contact: str):
        if not await self.api_controller.check_contact(contact):
            raise ContactNotFoundException()

        self.api_controller.contact = contact

        contact_info, (one_time_key, otk_idx) = await asyncio.gather(
            self.api_controller.get_contact_info(contact),
            self.api_controller.get_random_one_time_key(),
        )

        if not contact_info["success"]:
            print("Given contact does not exist!!")
            return

        if one_time_key is None:
            print("User has already used up his one time keys.")
            return

        contact_info = contact_info["user_data"]
        ephemeral_key = generate_DH()

        if contact_info["login"] != contact:
            AppControllerException(
                "Somehow you got wrong user! "
                f"You got {contact_info['login']} "
                f"rather than {contact}"
            )

        await self.api_controller.send_friend_request(
            {
                "my_login": self.user_state.login,
                "signature": self.user_state.signature,
                "contact_login": contact,
                "public_id_key": create_b64_from_public_key(
                    self.user_state.id_key.public_key()
                ).decode(PREFFERED_ENCODING),
                "public_ephemeral_key": create_b64_from_public_key(
                    ephemeral_key.public_key()
                ).decode(PREFFERED_ENCODING),
                "otk_index": otk_idx,
            }
        )

        if self.user_state.id_key is None:
            raise AppControllerException("somehow my id key dissapeard")

        shared_key = create_shared_key_X3DH_guest(
            self.user_state.id_key,
            ephemeral_key,
            create_public_key_from_b64(
                contact_info["public_id_key"].encode(PREFFERED_ENCODING)
            ),
            create_public_key_from_b64(
                contact_info["public_signed_pre_key"].encode(
                    PREFFERED_ENCODING
                )
            ),
            create_public_key_from_b64(
                one_time_key.encode(PREFFERED_ENCODING)
            ),
        )

        self.db_controller.add_contact(
            self.user_state,
            contact,
            contact_info["public_id_key"],
            binascii.b2a_base64(shared_key).decode(PREFFERED_ENCODING),
            contact_signed_pre_key=contact_info["public_signed_pre_key"],
            my_ephemeral_key=create_b64_from_private_key(ephemeral_key).decode(
                PREFFERED_ENCODING
            ),
            contact_otk_key=one_time_key,
        )
        print(f"You have send {contact} an invite")
