"""DANGER ZONE!
"""
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import HASH_SALT, SHARED_KEY_LENGTH, AEAD_NONCE
import binascii
from typing import Dict


def generate_DH() -> X25519PrivateKey:
    """
    Generate Diffie-Hellman key pair
    """
    return X25519PrivateKey.generate()


def hkdf(inp: bytes) -> bytes:
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


def dh(private_key: X25519PrivateKey, public_key: X25519PublicKey) -> bytes:
    out = private_key.exchange(public_key)
    return out


def aead_encrypt(key: bytes, message: bytes, additional_data: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(AEAD_NONCE, message, additional_data)


def aead_decrypt(key: bytes, message: bytes, additional_data: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(AEAD_NONCE, message, additional_data)


# --- HELPER FUNCTIONS


def create_header(
    public_key: X25519PublicKey, key_length: int, message_num: int
) -> Dict:
    return {
        "public_key": create_b64_from_public_key(public_key),
        "keylen": key_length,
        "number": message_num,
    }


def concatenate_msg(message: bytes, header: Dict) -> bytes:
    ...


def private_key_to_bytes(key: X25519PrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_to_bytes(key: X25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def create_b64_from_private_key(private_key: X25519PrivateKey) -> bytes:
    """Create b64 ascii string from private key object

    Args:
        private_key (X25519PrivateKey):
    Returns:
        bytes: b64 ascii string
    """
    private_bytes = private_key_to_bytes(private_key)
    b64_bytes = binascii.b2a_base64(private_bytes, newline=False)
    return b64_bytes


def create_private_key_from_b64(b64Key: bytes) -> X25519PrivateKey:
    """Derive X25519 Private key from b64 ascii string

    Args:
        b64Key (bytes): ascii encoded elliptic-curve key

    Returns:
        X25519PrivateKey: private key object
    """
    private_bytes = binascii.a2b_base64(b64Key)
    loaded_private_key = X25519PrivateKey.from_private_bytes(private_bytes)
    return loaded_private_key


def create_b64_from_public_key(private_key: X25519PublicKey) -> bytes:
    """Create b64 ascii string from private key object

    Args:
        private_key (X25519PrivateKey):
    Returns:
        bytes: b64 ascii string
    """
    public_bytes = public_key_to_bytes(private_key)
    b64_bytes = binascii.b2a_base64(public_bytes, newline=False)
    return b64_bytes


def create_public_key_from_b64(b64Key: bytes) -> X25519PublicKey:
    """Derive X25519 Private key from b64 ascii string

    Args:
        b64Key (bytes): ascii encoded elliptic-curve key

    Returns:
        X25519PrivateKey: private key object
    """
    public_bytes = binascii.a2b_base64(b64Key)
    loaded_private_key = X25519PublicKey.from_public_bytes(public_bytes)
    return loaded_private_key
