from .inner_ratchet import InnerRatchet
from typing import Optional


class RatchetSetException(Exception):
    ...

class RatchetSet:
    __slots__ = "_dh_ratchet", "_send_ratchet", "_recv_ratchet", "_root_ratchet"

    def __init__(self) -> None:
        self._root_ratchet:Optional[InnerRatchet] = None
        self._dh_ratchet:Optional[InnerRatchet] = None
        self._send_ratchet:Optional[InnerRatchet] = None
        self._recv_ratchet:Optional[InnerRatchet] = None

    
    @property
    def dh_ratchet(self) -> InnerRatchet:
        if self._dh_ratchet is None:
            raise RatchetSetException("Cannot access non existing DH ratchet")
        return self._dh_ratchet
        
    
    @property
    def send_ratchet(self):
        if self._send_ratchet is None:
            raise RatchetSetException("Cannot access non existing sending ratchet")
        return self._send_ratchet
    
    @property
    def recv_ratchet(self):
        if self._recv_ratchet is None:
            raise RatchetSetException("Cannot access non existing recieving ratchet")
        return self._recv_ratchet
    
    @property
    def root_ratchet(self):
        if self._root_ratchet is None:
            raise RatchetSetException("Cannot access non existing root ratchet")
        return self._root_ratchet

    @dh_ratchet.setter
    def dh_ratchet(self, ratchet:InnerRatchet) -> None:
        self._dh_ratchet = ratchet

    @send_ratchet.setter
    def send_ratchet(self, ratchet:InnerRatchet) -> None:
        self._send_ratchet = ratchet

    @recv_ratchet.setter
    def recv_ratchet(self, ratchet:InnerRatchet) -> None:
        self._recv_ratchet = ratchet

    @root_ratchet.setter
    def root_ratchet(self, ratchet:InnerRatchet) -> None:
        self._root_ratchet = ratchet