from .crypto_utils import hkdf
from app.config import RATCHET_STATE_KEY_LENGTH
from typing import Tuple
import binascii


class InnerRatchet:
    def __init__(self, initial_state: bytes) -> None:
        """
        Args:
            initial_state (bytes): According to signal
            documentation this key is the shared secret
            of two sides of the conversation.
        """
        self.state = initial_state

    def turn(self, inp: bytes = b"") -> Tuple[bytes, bytes]:
        output = hkdf(self.state + inp, RATCHET_STATE_KEY_LENGTH)
        new_root, chain_key = output[:32], output[32:]
        self.state = new_root
        return new_root, chain_key

    def get_snapshot(self) -> bytes:
        """
        THE ONLY THING THAT DEFINES THE
        RATCHET IT IS THE STATE. SO THE
        SNAPSHOT OF THE RATCHET IS ITS BASE64
        ENCODED STATE KEY
        """
        b64_encoded = binascii.b2a_base64(self.state, newline=False)
        return b64_encoded

    @staticmethod
    def from_snapshot(serialized: bytes) -> bytes:
        return binascii.a2b_base64(serialized)
