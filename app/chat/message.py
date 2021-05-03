class Message:
    __slots__ = "sender", "time_stamp", "body"

    def __init__(self, sender: str, time_stamp: str, body: str):
        self.sender: str = sender
        self.time_stamp: str = time_stamp
        self.body: str = body
