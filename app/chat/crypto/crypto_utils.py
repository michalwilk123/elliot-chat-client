from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


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
        salt=b"",
        info=b"",
        backend=default_backend(),
    )
    return hkdf.derive(inp)


def x3dh(
    id_public_key: X25519PrivateKey,
    signed_public_pre_key: X25519PrivateKey,
    one_time_public_key: X25519PrivateKey,
    guest_public_id_key: X25519PrivateKey,
    guest_public_ephemeral_key: X25519PrivateKey,
):
    """Performing the 4 Diffie-Hellman exchange"""
    dh1 = signed_public_pre_key.exchange(guest_public_id_key.public_key())
    dh2 = id_public_key.exchange(guest_public_ephemeral_key.public_key())
    dh3 = signed_public_pre_key.exchange(
        guest_public_ephemeral_key.public_key()
    )
    dh4 = one_time_public_key.exchange(guest_public_ephemeral_key.public_key())

    session_key = hkdf(dh1 + dh2 + dh3 + dh4, 32)
    return session_key
