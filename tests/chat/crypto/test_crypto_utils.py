from app.chat.crypto.crypto_utils import create_b64_from_key, create_key_from_b64, compare_keys
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def test_b642key_conversion():
    """parse random private key multiple times
    to check if any information is lost
    """
    dummy_key = X25519PrivateKey.generate()
    b64_dummy_key = create_b64_from_key(dummy_key)
    to_compare_key = create_key_from_b64(b64_dummy_key)
    assert compare_keys(dummy_key, to_compare_key)
    assert b64_dummy_key == create_b64_from_key(to_compare_key)