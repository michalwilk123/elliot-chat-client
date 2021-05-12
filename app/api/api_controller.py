from app.chat.crypto_controller import CryptoController
import binascii
from app.chat.crypto.crypto_utils import (
    create_b64_from_private_key,
    create_b64_from_public_key,
    create_private_key_from_b64,
    create_public_key_from_b64,
    create_shared_key_X3DH_establisher,
)
from app.routes import ApiRoutes
from app.config import (
    DEFAULT_DB_PATH,
    FETCH_DELAY_PERIOD,
    MAX_ONE_TIME_KEYS,
    PREFFERED_ENCODING,
    SERVER_URL,
)
from typing import Optional, Tuple, List
from aiohttp.client import ClientSession
from app.user.user_state import UserState
import random
from app.database.db_controller import DatabaseController
import asyncio


class ApiControllerException(Exception):
    ...


class ApiController:
    def __init__(
        self,
        user_state: UserState,
        db_controller: DatabaseController,
        /,
        url: str = SERVER_URL,
        init_session: bool = True,
        register_user: bool = False,
        db_path: str = DEFAULT_DB_PATH,
    ) -> None:
        self._client_session: Optional[ClientSession] = (
            ClientSession() if init_session else None
        )
        self.user_state = user_state
        self._url = url
        self.db_controller = db_controller
        self._contact: Optional[str] = None
        self.register_user = register_user
        self.db_path = db_path

    @property
    def contact(self) -> str:
        if self._contact is not None:
            return self._contact
        else:
            raise ApiControllerException("Contact property not set!!!")

    @contact.setter
    def contact(self, contact: str) -> None:
        self._contact = contact

    @property
    def client_session(self) -> ClientSession:
        if self._client_session is None:
            raise ApiControllerException("client session not set!")
        return self._client_session

    @property
    def url(self) -> str:
        return self._url

    async def end(self):
        await self.client_session.close()

    async def server_task(self):
        if self.register_user:
            await self.create_user()

        while True:
            await self.resolve_new_contacts(),
            await asyncio.sleep(FETCH_DELAY_PERIOD)

    async def estabish_self_to_server(self):
        user_model = {
            "login": self.user_state.login,
            "public_id_key": create_b64_from_public_key(
                self.user_state.id_key.public_key()
            ),
            "public_signed_pre_key": create_b64_from_public_key(
                self.user_state.signed_pre_key.public_key()
            ),
            "signature": self.user_state.signature,
            "number_of_otk": MAX_ONE_TIME_KEYS,
            "one_time_keys": None,
        }
        async with self.client_session.post(
            ApiRoutes.USER_OPER, json=user_model
        ) as resp:
            if resp.status == 200:
                print(f"Successfuly added new user: {self.user_state.login}")
            else:
                print(f"Could not add user {self.user_state.login}")
                print(await resp.text())
                raise ApiControllerException("Could not add user!!")

    async def establish_initial_otk(self, otk_initial: dict):
        async with self.client_session.post(
            self._url + ApiRoutes.ONE_TIME_KEY, json=otk_initial
        ) as resp:
            if resp.status == 200:
                print(
                    "Finish one time key setup. "
                    f"Got response: {await resp.json()}"
                )
            else:
                print("Could not setup otk keys")
                print(await resp.text())

    async def create_user(self):
        await self.estabish_self_to_server()

        otk_keys = []
        for priv_key in self.db_controller.get_user_otk(self.user_state):
            otk_keys.append(
                create_b64_from_public_key(
                    create_private_key_from_b64(priv_key).public_key()
                )
            )

        assert (
            len(otk_keys) == MAX_ONE_TIME_KEYS
        ), "Otk keys are not initialized!!"

        otk_initial = {
            "login": self.user_state.login,
            "signature": self.user_state.signature,
            "num_of_keys": MAX_ONE_TIME_KEYS,
            "one_time_public_keys": otk_keys,
        }
        await self.establish_initial_otk(otk_initial)

    def approve_new_contact(self, invite: dict) -> str:
        curr_otk, new_otk = self.db_controller.replace_one_time_key(
            self.user_state, invite["otk_index"]
        )
        new_otk_b64 = create_b64_from_private_key(new_otk).decode(
            PREFFERED_ENCODING
        )

        if (
            self.user_state.id_key is None
            or self.user_state.signed_pre_key is None
        ):
            raise ApiControllerException("All user keys must be present!")

        print(
            "BOGDAN OTK KEY: ",
            create_b64_from_public_key(curr_otk.public_key()),
        )

        shared_key = create_shared_key_X3DH_establisher(
            self.user_state.id_key,
            self.user_state.signed_pre_key,
            curr_otk,
            create_public_key_from_b64(invite["public_id_key"]),
            create_public_key_from_b64(invite["public_ephemeral_key"]),
        )

        self.db_controller.add_contact(
            self.user_state,
            invite["my_login"],
            invite["public_id_key"],
            binascii.b2a_base64(shared_key).decode(PREFFERED_ENCODING),
            contact_ephemeral_key=invite["public_ephemeral_key"],
            my_otk_key=create_b64_from_private_key(curr_otk).decode(
                PREFFERED_ENCODING
            ),
        )
        self.init_ratchet_configuration(invite["my_login"])

        return new_otk_b64

    def init_ratchet_configuration(self, login:str):
        crypto_controller = CryptoController(
            self.user_state,
            login,
            DB_PATH=self.db_path,
        )
        crypto_controller.init_ratchets(
            opt_private_key=self.user_state.signed_pre_key
        )

    async def send_friend_request(self, invite: dict):
        async with self.client_session.post(
            self._url + ApiRoutes.CONTACT_OPER, json=invite
        ) as resp:
            result = await resp.json()

    async def resolve_new_contacts(self):
        params = {
            "login": self.user_state.login,
            "signature": self.user_state.signature.decode(PREFFERED_ENCODING),
        }
        async with self.client_session.get(
            self._url + ApiRoutes.CONTACT_OPER, params=params
        ) as resp:
            if resp.status == 200:
                inv_list = list((await resp.json())["invites"])
                if inv_list:
                    print(f"Got {len(inv_list)} new invites!")
            else:
                print("Could not retrieve new pending invites!")
                print(await resp.text())
                return
        for invite in inv_list:
            new_otk = self.approve_new_contact(invite)
            otk_model = {
                "login": self.user_state.login,
                "signature": self.user_state.signature.decode(
                    PREFFERED_ENCODING
                ),
                "one_time_public_key": new_otk,
                "otk_index": invite["otk_index"],
            }
            async with self.client_session.put(
                self._url + ApiRoutes.ONE_TIME_KEY, json=otk_model
            ) as resp:
                if resp.status == 200:
                    print(await resp.json())
                else:
                    print(f"Could not set otk key: {await resp.text()}")

    async def check_contact(self, contact: str) -> bool:
        async with self.client_session.get(
            self._url + ApiRoutes.USER_OPER, params={"login": contact}
        ) as resp:
            return resp.status == 200

    async def init_conversation(self, message_queue: asyncio.Queue) -> None:
        data = {
            "login": self.user_state.login,
            "signature": self.user_state.signature,
        }
        async with self.client_session.get(
            self._url + ApiRoutes.CHAT_OPER, json=data
        ) as resp:
            for m in (await resp.json())["pending_messages"]:
                # TODO : might be problematic.
                # Dont know the sequence of messages
                await message_queue.put(m)

    async def get_contact_info(self, contact: str):
        async with self.client_session.get(
            self._url + ApiRoutes.USER_OPER, params={"login": contact}
        ) as resp:
            return await resp.json()

    async def get_random_one_time_key(
        self,
    ) -> Tuple[Optional[str], int]:
        async with self.client_session.get(
            self._url + ApiRoutes.ONE_TIME_KEY_LIST,
            params={"contact": self.contact},
        ) as resp:
            if resp.status == 200:
                avail_list: List[int] = (await resp.json())[
                    "available_indexes"
                ]
            else:
                print(await resp.text())
                return None, resp.status

        rand_idx = random.choice(avail_list)

        async with self.client_session.get(
            self._url + ApiRoutes.ONE_TIME_KEY,
            params={"login": self.contact, "index": rand_idx},
        ) as resp:
            if resp.status == 200:
                key: str = (await resp.json())["one_time_key"]
            else:
                print(await resp.text())
                return None, resp.status

        return key, rand_idx
