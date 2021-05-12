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
from cryptography.hazmat.primitives.padding import PKCS7
from app.config import HASH_SALT, AEAD_NONCE, BLOCK_SIZE, SHARED_KEY_LENGTH
import binascii


def generate_DH() -> X25519PrivateKey:
    """
    Generate Diffie-Hellman key pair.
    The riddle for the diffie hellman is
    Elliptic Curve problem
    """
    return X25519PrivateKey.generate()


def hkdf(inp: bytes, length: int) -> bytes:
    """
    Reduce combined bytes input into limited length
    bytestring key
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=HASH_SALT,
        info=b"",
        backend=default_backend(),
    )
    return hkdf.derive(inp)


def dh(private_key: X25519PrivateKey, public_key: X25519PublicKey) -> bytes:
    out = private_key.exchange(public_key)
    return out


def aead_encrypt(
    key: bytes,
    message: bytes,
    additional_data: bytes = b"",
    /,
    pad: bool = False,
) -> bytes:
    if pad:
        padder = PKCS7(BLOCK_SIZE).padder()
        padded_key = padder.update(key)
        padded_key += padder.finalize()
        key = padded_key

    aesgcm = AESGCM(key)
    return aesgcm.encrypt(AEAD_NONCE, message, additional_data)


def aead_decrypt(
    key: bytes,
    message: bytes,
    additional_data: bytes = b"",
    /,
    pad: bool = False,
) -> bytes:
    if pad:
        padder = PKCS7(BLOCK_SIZE).padder()
        padded_key = padder.update(key)
        padded_key += padder.finalize()
        key = padded_key

    aesgcm = AESGCM(key)
    return aesgcm.decrypt(AEAD_NONCE, message, additional_data)


def create_shared_key_X3DH_guest(
    my_private_id_key: X25519PrivateKey,
    my_private_ephemeral_key: X25519PrivateKey,
    estab_public_id_key: X25519PublicKey,
    estab_public_signed_pre_key: X25519PublicKey,
    estab_public_one_time_key: X25519PublicKey,
) -> bytes:

    """the 3 diffie hellman key exchange
    from the perspective of someone who is an
    initiator of the conversation
    """
    dh1 = my_private_id_key.exchange(estab_public_signed_pre_key)
    dh2 = my_private_ephemeral_key.exchange(estab_public_id_key)
    dh3 = my_private_ephemeral_key.exchange(estab_public_signed_pre_key)
    dh4 = my_private_ephemeral_key.exchange(estab_public_one_time_key)

    # the shared key is KDF(DH1||DH2||DH3||DH4)
    shared_key = hkdf(dh1 + dh2 + dh3 + dh4, SHARED_KEY_LENGTH)
    return shared_key


def create_shared_key_X3DH_establisher(
    my_private_id_key: X25519PrivateKey,
    my_private_signed_pre_key: X25519PrivateKey,
    my_private_one_time_key: X25519PrivateKey,
    guest_public_id_key: X25519PublicKey,
    guest_public_ephemeral_key: X25519PublicKey,
) -> bytes:
    dh1 = my_private_signed_pre_key.exchange(guest_public_id_key)
    dh2 = my_private_id_key.exchange(guest_public_ephemeral_key)
    dh3 = my_private_signed_pre_key.exchange(guest_public_ephemeral_key)
    dh4 = my_private_one_time_key.exchange(guest_public_ephemeral_key)

    # the shared key is KDF(DH1||DH2||DH3||DH4)
    shared_key = hkdf(dh1 + dh2 + dh3 + dh4, SHARED_KEY_LENGTH)
    return shared_key


# --- HELPER FUNCTIONS


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


def create_b64_from_public_key(public_key: X25519PublicKey) -> bytes:
    """Create b64 ascii string from private key object

    Args:
        private_key (X25519PrivateKey):
    Returns:
        bytes: b64 ascii string
    """
    public_bytes = public_key_to_bytes(public_key)
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
