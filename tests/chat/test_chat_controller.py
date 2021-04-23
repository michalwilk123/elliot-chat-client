from app.chat.chat_controller import ChatController
from app.user_state import UserState 
import re
import asyncio
import pytest
from unittest.mock import AsyncMock

def test_get_timestamp():
    expr = re.search(
        "[0-9]{2}:[0-9]{2}:[0-9]{2}",
        ChatController.get_timestamp()
    )
    assert expr is not None
    

@pytest.mark.asyncio
async def test_websocket_worker(mocker):
    state = UserState("alice", "password")
    chat_controller = ChatController(state, "bob")

    chat_controller.messageQueue = asyncio.Queue()

    async def get_message_side_effect():
        return "Message1234"

    mocker.patch(
        'app.api.websocket_controller.WebSocketController.get_message',
        side_effect = get_message_side_effect
    )

    task = asyncio.create_task(chat_controller.websocket_worker())
    result = await asyncio.wait_for(
        chat_controller.messageQueue.get(), 2
    )
    task.cancel()
    chat_controller.messageQueue.task_done()
    
    assert result.sender == 'bob'
    assert result.body == 'Message1234'


