from app.chat.crypto.crypto_utils import (
    create_b64_from_private_key,
    create_private_key_from_b64,
    private_key_to_bytes,
    aead_encrypt,
    aead_decrypt,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def test_b64_2_private_key_conversion():
    """parse random private key multiple times
    to check if any information is lost
    """
    dummy_key = X25519PrivateKey.generate()
    b64_dummy_key = create_b64_from_private_key(dummy_key)
    to_compare_key = create_private_key_from_b64(b64_dummy_key)
    assert private_key_to_bytes(dummy_key) == private_key_to_bytes(
        to_compare_key
    )
    assert b64_dummy_key == create_b64_from_private_key(to_compare_key)


def test_aead_encryption():
    test_text = "mn,XCZCXZ ąćźśęŁÓŃ↑↑↑↑".encode("utf-8")
    some_key = "jeste klucze".encode("utf-8")

    enc = aead_encrypt(some_key, test_text, pad=True)

    decrypted = aead_decrypt(some_key, enc, pad=True)
    assert test_text == decrypted
