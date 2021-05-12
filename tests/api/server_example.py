import asyncio
from aiohttp import web, WSMsgType


async def websocket_handler(request):
    print("Websocket connection starting")
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print("Websocket connection ready")

    async for msg in ws:
        print(msg)
        if msg.type == WSMsgType.TEXT:
            print(msg.data)
            if msg.data == "close":
                await ws.close()
            else:
                await ws.send_str(msg.data + "/answer")

    return ws


app = web.Application()
app.router.add_route("GET", "/ws", websocket_handler)
web.run_app(app, host="localhost", port=8001)
