"""
Dangerous functions used for ee2e encryption.
Highly influenced by:
https://nfil.dev/coding/encryption/python/double-ratchet-example/
"""
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend


def b64(msg):
    # base64 encoding helper function
    return base64.encodebytes(msg).decode('utf-8').strip()

def hkdf(inp, length):
    # use HKDF on an input to derive a key
    hkdf = HKDF(algorithm=hashes.SHA256(), length=length, salt=b'',
                info=b'', backend=default_backend())
    return hkdf.derive(inp)

def x3dh(self, alice):
    # perform the 4 Diffie Hellman exchanges (X3DH)
    dh1 = self.SPKb.exchange(alice.IKa.public_key())
    dh2 = self.IKb.exchange(alice.EKa.public_key())
    dh3 = self.SPKb.exchange(alice.EKa.public_key())
    dh4 = self.OPKb.exchange(alice.EKa.public_key())
    # the shared key is KDF(DH1||DH2||DH3||DH4)
    self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
    print('[Bob]\tShared key:', b64(self.sk))