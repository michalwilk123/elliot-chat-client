from app.user_state import UserState


class InnerRatchet:
    def __init__(self, initial_state: bytes) -> None:
        """
        Args:
            initial_state (bytes): According to signal 
            documentation this key is the shared secret 
            of two sides of the conversation.
        """
        pass

    def get_snapshot(self) -> bytes:
        ...


class EncryptedUser:
    def __init__(self, user_state: UserState) -> None:
        self.user_state = user_state
