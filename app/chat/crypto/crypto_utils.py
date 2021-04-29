from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from app.config import HASH_SALT
import binascii


def generate_private_key() -> X25519PrivateKey:
    """
    we might change the curve or alghorithm so this functionality
    is abstracted
    """
    return X25519PrivateKey.generate()


def hkdf(inp, length) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=HASH_SALT,
        info=b"",
        backend=default_backend(),
    )
    return hkdf.derive(inp)


def create_b64_from_key(private_key: X25519PrivateKey) -> bytes:
    """Create b64 ascii string from private key object

    Args:
        private_key (X25519PrivateKey):
    Returns:
        bytes: b64 ascii string
    """
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
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
