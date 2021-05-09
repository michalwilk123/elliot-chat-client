from app.api.api_controller import ApiController
from .crypto_controller import CryptoController, CryptoControllerException
from app.cli.message import Message
from app.cli.chat import display_message
from app.cli.utilities import get_timestamp
import asyncio
import aioconsole


class ChatController:
    def __init__(
        self,
        api_controller: ApiController,
        partner: str,
    ):
        self.partner = partner
        self.user_state = api_controller.user_state
        self.api_controller = api_controller
        self.crypto_controller = CryptoController(self.user_state, partner)

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_workers())

    def __del__(self):
        # i know that this code is dumb :/
        if not self.websocket_con.closed:
            print("This should be closed in normal way :/")
            asyncio.get_event_loop().run_until_complete(
                self.websocket_con.close()
            )

    async def init_ws_connection(self):
        self.messageQueue = asyncio.Queue()
        await self.api_controller.init_conversation(self.messageQueue)

        self.websocket_con = (
            await self.api_controller.client_session.ws_connect(
                self.api_controller.url
            )
        )

    async def run_workers(self):
        # asyncio.queue needs an event_loop so we declare it right
        # here, rather than in constructor

        await self.init_ws_connection()

        ws_task = asyncio.create_task(self.websocket_worker())
        ui_task = asyncio.create_task(self.user_input_worker())

        # whole chat is alive till the user chooses to end it
        await ui_task
        ws_task.cancel()
        await self.websocket_con.close()
        self.messageQueue.task_done()

        asyncio.gather(ws_task, ui_task, return_exceptions=True)

    async def websocket_worker(self):
        while True:
            output = await self.websocket_con.receive_json()

            # the decryption is done at that exact moment
            try:
                translated: str = self.crypto_controller.decrypt_json_message(
                    output
                )
                message = Message(self.partner, get_timestamp(), translated)
            except CryptoControllerException as e:
                message = Message(self.partner, get_timestamp(), str(e))

            await self.messageQueue.put(message)

    async def user_input_worker(self):
        """This worker decides about the life of the event loop"""
        end = False
        erase = "\x1b[1A\x1b[2K"

        while True:
            while not self.messageQueue.empty():
                vis_message = await self.messageQueue.get()
                display_message(vis_message)

            if end:
                print(f"Ending chat with user { self.partner }")
                break

            # we check if :q is pressed, if yes we end the chat service
            in_message = await aioconsole.ainput("")
            # we are erasing raw input text the user has just made
            print(erase, end="")

            if in_message == ":q":
                end = True

            if in_message:
                # sending raw message to the ws controller to be send by
                # the websocket to the end reciever
                # await self._websocket_controller.send_message(in_message)
                await self.websocket_con.send_json(
                    self.crypto_controller.encrypt_to_json_message(in_message)
                )

                # we put user message on the screen
                # we can only access the screen by the message queue
                # so we put it here
                await self.messageQueue.put(
                    Message(
                        self.user_state.login,
                        get_timestamp(),
                        in_message,
                        # we display the user input and not
                        # what is actually send to second user
                    )
                )
