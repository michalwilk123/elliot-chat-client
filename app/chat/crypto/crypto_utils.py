"""DANGER ZONE!
"""
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from app.config import HASH_SALT, SHARED_KEY_LENGTH
import binascii
from typing import Dict


def generate_DH() -> X25519PrivateKey:
    """
    Generate Diffie-Hellman key pair
    """
    return X25519PrivateKey.generate()


def hkdf(inp:bytes) -> bytes:
    """
    Reduce combined bytes input into limited length
    bytestring key
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=SHARED_KEY_LENGTH,
        salt=HASH_SALT,
        info=b"",
        backend=default_backend(),
    )
    return hkdf.derive(inp)


def dh(private_key:X25519PrivateKey, public_key:X25519PublicKey) -> bytes:
    out = private_key.exchange(public_key)
    return out

def aead_encrypt(key:bytes, message:bytes, additional_data:bytes):
    ...

def aead_decrypt(key:bytes, message:bytes, additional_data:bytes):
    ...

# --- HELPER FUNCTIONS

def create_header(public_key:X25519PublicKey, key_length:int, message_num:int):
    ...

def concatenate_msg(message:bytes, header:Dict) -> bytes:
    ...



def key_to_bytes(key:X25519PrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )


def compare_keys(key1:X25519PrivateKey, key2:X25519PrivateKey) -> bool:
    key1_bin = key_to_bytes(key1)
    key2_bin = key_to_bytes(key2)
    return key1_bin == key2_bin


def create_b64_from_key(private_key: X25519PrivateKey) -> bytes:
    """Create b64 ascii string from private key object

    Args:
        private_key (X25519PrivateKey):
    Returns:
        bytes: b64 ascii string
    """
    private_bytes = key_to_bytes(private_key)
    b64_bytes = binascii.b2a_base64(private_bytes, newline=False)
    return b64_bytes


def create_key_from_b64(b64Key: bytes) -> X25519PrivateKey:
    """Derive X25519 Private key from b64 ascii string

    Args:
        b64Key (bytes): ascii encoded elliptic-curve key

    Returns:
        X25519PrivateKey: private key object
    """
    private_bytes = binascii.a2b_base64(b64Key)
    loaded_private_key = X25519PrivateKey.from_private_bytes(private_bytes)
    return loaded_private_key
