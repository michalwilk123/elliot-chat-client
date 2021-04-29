"""Tests related with the low level websocket connection with mocked 
server. 
Tests for establishing connection, closing connection and ensuring
that message data throughout the app is not modified
"""
from websockets.client import WebSocketClientProtocol
from app.api.websocket_controller import (
    WebSocketController,
    NotConnectedToWSHostException,
    MultipleWSHostClose,
)
from app.user_state import UserState
import pytest
import asyncio
import subprocess


@pytest.mark.asyncio
async def test_establish_connection():
    # integrity test - checking if the client is connectiong to sockets properly

    p = subprocess.Popen(
        ["pipenv", "run", "python", "tests/api/server_example.py"]
    )

    # this may cause issues. Server process must be created before
    # we start the connection. I cannot find the way to block this 
    # function till the server is created so i just wait for one second here
    await asyncio.sleep(1)
    alice_state = UserState("alice", "passw")
    ws_controller = WebSocketController(alice_state, "bob")
    await ws_controller.establish_connection()
    assert ws_controller.connection_status()
    await ws_controller.close_connection()
    assert not ws_controller.connection_status()
    p.kill()


@pytest.mark.asyncio
async def test_send_raw_message(mocker):
    message_list = []

    def send_side_effect(body):
        nonlocal message_list
        message_list.append(body.decode("utf-8"))

    mocker.patch(
        "websockets.WebSocketClientProtocol.send", side_effect=send_side_effect
    )

    alice_state = UserState("alice", "passw")
    ws_controller = WebSocketController(alice_state, "bob")
    ws_controller.websocket_proto = WebSocketClientProtocol()

    raw_message = "hello, hello greetings from the underground 123"
    await ws_controller._send_raw_message(raw_message)
    assert message_list[0] == raw_message


@pytest.mark.asyncio
async def test_get_message(mocker):
    toRecieve = ["message1", "message2", "message3"]
    recieved = toRecieve[::-1]

    async def recv_side_effect():
        nonlocal toRecieve
        await asyncio.sleep(0.1)
        return toRecieve.pop()

    mocker.patch(
        "websockets.WebSocketClientProtocol.recv", side_effect=recv_side_effect
    )

    alice_state = UserState("alice", "passw")
    ws_controller = WebSocketController(alice_state, "bob")
    ws_controller.websocket_proto = WebSocketClientProtocol()

    for val in recieved:
        msg = await ws_controller.get_message()
        assert val == msg


@pytest.mark.asyncio
async def test_should_throw_when_no_connection():
    alice_state = UserState("alice", "passw")
    ws_controller = WebSocketController(alice_state, "bob")

    with pytest.raises(NotConnectedToWSHostException):
        await ws_controller.send_message("test message")


@pytest.mark.asyncio
async def test_should_throw_on_multiple_close(mocker):
    alice_state = UserState("alice", "passw")
    ws_controller = WebSocketController(alice_state, "bob")

    async def mocked_establish_connection(url):
        return WebSocketClientProtocol()

    # mocking connection to the server
    mocker.patch("websockets.connect", side_effect=mocked_establish_connection)

    # mocking closing connection to not have any effect
    mocker.patch(
        "websockets.WebSocketClientProtocol.close", side_effect=lambda: ...
    )

    await ws_controller.establish_connection()
    await ws_controller.close_connection()

    with pytest.raises(MultipleWSHostClose):
        await ws_controller.close_connection()
