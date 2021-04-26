import asyncio
import websockets


async def connected(websocket, path: str):
    """Simple server:
    recieves text and echos it back to the client

    Args:
        websocket ([type]): [description]
        path (str): [description]
    """
    name = await websocket.recv()
    greeting = name.upper() + "FROM: " + path
    await websocket.send(greeting)


print("starting server")
start_server = websockets.serve(connected, "localhost", 8001)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
print("ending server")
