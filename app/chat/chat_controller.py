from app.api.websocket_controller import WebSocketController
from .message import Message
from app.user_state import UserState
import asyncio
from datetime import datetime
import aioconsole

class ChatController:
    def __init__(self, user_state:UserState, reciever:str):
        self._websocket_controller = WebSocketController(user_state, reciever)
        self.reciever = reciever
        self.user_state = user_state


    @staticmethod
    def _display_message(message:Message, pretty:bool=True):
        if message.body == '':
            pass 
        elif pretty:
            print(f"{message.sender}  {message.time_stamp} - {message.body}")
        else:
            print(f"FFF{message.time_stamp} <{message.sender}> {message.body}")

    @staticmethod
    def get_timestamp() -> str:
        now = datetime.now()
        return now.strftime('%H:%M:%S')

    def start(self):
        asyncio.run(self.run_workers())
    
    async def run_workers(self):
        # asyncio.queue needs an event_loop so we declare it right
        # here, rather than in constructor
        self.messageQueue =asyncio.Queue()

        await self._websocket_controller.establish_connection()
        

        ws_task = asyncio.create_task(self.websocket_worker())
        ui_task = asyncio.create_task(self.user_input_worker())

        # whole chat is alive till the user chooses to end it
        await ui_task
        ws_task.cancel()
        await self._websocket_controller.close_connection()
        self.messageQueue.task_done()

        asyncio.gather(ws_task, ui_task, return_exceptions=True)


    async def websocket_worker(self):
        while True:
            message = await self._websocket_controller.get_message()
            await self.messageQueue.put(Message(
                self.reciever,
                ChatController.get_timestamp(),
                message
            ))


    async def user_input_worker(self):
        end = False
        erase = '\x1b[1A\x1b[2K'

        while True:
            while not self.messageQueue.empty():
                vis_message = await self.messageQueue.get()
                ChatController._display_message(vis_message)
            
            if end:
                print(f'Ending chat with user { self.reciever }')
                break
            
            # we check if :q is pressed, if yes we end the chat service
            in_message = await aioconsole.ainput("")
            # in_message = input("")
            # we are erasing raw input text the user has just made
            print(erase, end="")

            if in_message == ':q':
                end = True
            
            if in_message != '':
                # sending raw message to the ws controller to be send by
                # the websocket to the end reciever
                await self._websocket_controller.send_message(in_message)

                # we put user message on the screen 
                # we can only access the screen by the message queue
                # so we put it here
                await self.messageQueue.put(Message(
                    self.user_state.login,
                    ChatController.get_timestamp(),
                    in_message
                ))
