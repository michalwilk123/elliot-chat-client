from app.chat.crypto.crypto_utils import create_public_key_from_b64
from app.config import PREFFERED_ENCODING
from .chat_member import ChatMember
from .crypto.establisher import Establisher
from app.api.websocket_controller import WebSocketController
from .message import Message
from app.user_state import UserState
from app.api.response_parser import parse_respose, ResponseType, build_response
import asyncio
from datetime import datetime
import aioconsole


class ChatController:
    def __init__(
        self, user_state: UserState, partner: str, establisher: Establisher
    ):
        self._websocket_controller = WebSocketController(user_state, partner)
        self.establisher = establisher
        self.partner = partner
        self.user_state = user_state
        self.chat_session = ChatMember(user_state, partner)

    @staticmethod
    def _display_message(message: Message, pretty: bool = True):
        if message.body == "":
            pass
        elif pretty:
            print(f"{message.sender}  {message.time_stamp} - {message.body}")
        else:
            print(f"FFF{message.time_stamp} <{message.sender}> {message.body}")

    @staticmethod
    def get_timestamp() -> str:
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def start(self):
        asyncio.run(self.run_workers())

    async def run_workers(self):
        # asyncio.queue needs an event_loop so we declare it right
        # here, rather than in constructor
        self.messageQueue = asyncio.Queue()
        self.new_contacts_queue = asyncio.Queue()

        await self._websocket_controller.establish_connection()

        ws_task = asyncio.create_task(self.websocket_worker())
        ui_task = asyncio.create_task(self.user_input_worker())
        new_contacts_task = asyncio.create_task(self.new_contacts_task())

        # whole chat is alive till the user chooses to end it
        await ui_task
        ws_task.cancel()
        new_contacts_task.cancel()
        await self._websocket_controller.close_connection()
        self.messageQueue.task_done()
        self.new_contacts_queue.task_done()

        asyncio.gather(
            ws_task, ui_task, new_contacts_task, return_exceptions=True
        )

    async def websocket_worker(self):
        while True:
            raw_output = await self._websocket_controller.get_message()
            out = parse_respose(raw_output)
            if out["head"]["type"] == ResponseType.MESSAGE:
                await self.messageQueue.put(
                    Message(
                        self.partner,
                        ChatController.get_timestamp(),
                        out["body"]["content"],
                    )
                )
            elif out["head"]["type"] == ResponseType.X3DH_SESSION_START:
                await self.new_contacts_queue.put(out)

    async def user_input_worker(self):
        """This worker decides about the life of the event loop"""
        end = False
        erase = "\x1b[1A\x1b[2K"

        while True:
            while not self.messageQueue.empty():
                vis_message = await self.messageQueue.get()
                ChatController._display_message(vis_message)

            if end:
                print(f"Ending chat with user { self.partner }")
                break

            # we check if :q is pressed, if yes we end the chat service
            in_message = await aioconsole.ainput("")
            # in_message = input("")
            # we are erasing raw input text the user has just made
            print(erase, end="")

            if in_message == ":q":
                end = True

            if in_message != "":
                # sending raw message to the ws controller to be send by
                # the websocket to the end reciever
                await self._websocket_controller.send_message(in_message)

                # we put user message on the screen
                # we can only access the screen by the message queue
                # so we put it here
                await self.messageQueue.put(
                    Message(
                        self.user_state.login,
                        ChatController.get_timestamp(),
                        in_message,
                    )
                )

    async def new_contacts_task(self):
        while True:
            """
            Creating new key according to the test case:
            test_starting_conversation.py
            """
            new_contact = await self.new_contacts_queue.get()
            self.establisher.create_shared_key_X3DH(
                create_public_key_from_b64(
                    new_contact["body"]["public_id_key"].encode(
                        PREFFERED_ENCODING
                    )
                ),
                create_public_key_from_b64(
                    new_contact["body"]["public_ephemeral_key"].encode(
                        PREFFERED_ENCODING
                    )
                ),
            )
            self.establisher.set_one_time_key(new_contact["body"]["one_time_key_index"])
            keys_dict = {
                "public_id_key" : self.establisher.get_public_id_key(),
                "public_signed_prekey" : self.establisher.get_public_signed_key(),
                "public_one_time_key" : self.establisher.get_public_one_time_key()
            }
            self.establisher.save()

            guest_response = build_response(
                self.user_state,
                type=ResponseType.X3DH_SESSION_HANDSHAKE,
                keyes = keys_dict
            )
            await self._websocket_controller.send_message(guest_response)
