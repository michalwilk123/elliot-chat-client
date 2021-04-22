import websockets
import requests
import asyncio
from random import choice

class WebSocketController:
    def __init__(self, user_state, user_id):
        """
        this wil actually send a message to someone.
        Message transportation functionality
        """
        self.m_q = ["aaa", "bbbb", "cc", "ddddddddd", "eeeeeee"]

    async def establish_connection(self):
        """
        Test if connection with the server exists
        """
        print("connecting")
    
    async def get_message(self) -> str:
        """Get readable message from the chat guest
        Returns:
            str: decoded message string
        """
        await asyncio.sleep(1)
        return choice(self.m_q)


    async def close_connection(self):
        await asyncio.sleep(1)
        print('connection ended')

    async def send_message(self, message_body:str):
        """Send message to the guest

        Args:
            message_body (str): raw, not encrypted message
        """
        await asyncio.sleep(1)