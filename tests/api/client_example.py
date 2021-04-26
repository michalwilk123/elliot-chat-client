import asyncio
import websockets

async def hello():
    con = await websockets.connect('ws://localhost:8765')
    name = input("What's your name? ")
    await con.send(name)
    print("> {}".format(name))

    greeting = await con.recv()
    print("< {}".format(greeting))

    await con.close()

    # async with websockets.connect('ws://localhost:8765') as websocket:


asyncio.get_event_loop().run_until_complete(hello())