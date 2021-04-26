import websockets
import asyncio

from websockets.client import WebSocketClientProtocol
from app.user_state import UserState
from random import choice
from app.config import SERVER_URL


class NotConnectedToWSHostException(Exception):
    ...

class MultipleWSHostClose(Exception):
    ...

class WebSocketController:
    def __init__(self, user_state:UserState, reciever_login:str):
        """
        this wil actually send a message to someone.
        Message transportation functionality
        """
        self.connected:bool = False

    async def establish_connection(self, server_url:str=SERVER_URL):
        """
        Test if connection with the server exists.
        """
        self.websocket_proto = await websockets.connect(server_url)
        self.connected = True

    async def get_message(self) -> str:
        """Get readable message from the server
        Returns:
            str: decoded message string
        """
        message = str(await self.websocket_proto.recv())
        return message


    async def close_connection(self):
        if not self.connection_status():
            raise MultipleWSHostClose("You cannot close closed websocket")
        await self.websocket_proto.close()
        self.connected = False
        print('connection ended')

    async def _send_raw_message(self, message_body:str):
        """This method is responsible for sending 
        encrypted message to peer.
        Does not change its contents.

        Args:
            message_body (str): raw text message 

        Throw error when message had problems
        """
        await self.websocket_proto.send(message_body.encode("utf-8"))


    async def send_message(self, message_body:str):
        """Send message to the guest. Throw error when not
        connected to the server

        Args:
            message_body (str): raw, not encrypted message
        """
        if not self.connected:
            raise NotConnectedToWSHostException("cannot send message to not connected server. Be sure you established a connection!")
        ## ---  encryption ---
        await self._send_raw_message(message_body)

    def connection_status(self) -> bool:
        if not hasattr(self, "connected"):
            return False
        
        return self.connected