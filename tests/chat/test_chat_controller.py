# ???????????????
# def test_get_timestamp():
#     expr = re.search(
#         "[0-9]{2}:[0-9]{2}:[0-9]{2}", get_timestamp()
#     )
#     assert expr is not None


# @pytest.mark.asyncio
# async def test_websocket_worker(mocker):

#     state = UserState("alice", "password")
#     api_controller = ApiController(state, url=TEST_SITE)
#     chat_controller = ChatController(state, api_controller, "bob")

#     chat_controller.messageQueue = asyncio.Queue(maxsize=1)

#     async def get_message_side_effect():
#         return "Message1234"

#     mocker.patch(
#         "app.api.websocket_controller.WebSocketController.get_message",
#         side_effect=get_message_side_effect,
#     )

#     task = asyncio.create_task(chat_controller.websocket_worker())
#     result = await asyncio.wait_for(chat_controller.messageQueue.get(), 2)
#     task.cancel()
#     chat_controller.messageQueue.task_done()

#     assert result.sender == "bob"
#     assert result.body == "Message1234"
