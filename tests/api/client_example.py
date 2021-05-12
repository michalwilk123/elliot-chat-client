import asyncio
from aiohttp import ClientSession, WSMsgType


async def start_client():
    session = ClientSession()
    async with session.ws_connect("http://localhost:8001/ws") as ws:
        msg = input("message to send: ")
        await ws.send_str(msg)

        async for msg_response in ws:
            print(f"Message recieved: {msg_response.data}")
            msg = input("message to send: ")
            await ws.send_str(msg)

            if msg_response in (WSMsgType.CLOSED, WSMsgType.ERROR):
                break


loop = asyncio.get_event_loop()
loop.run_until_complete(start_client())
