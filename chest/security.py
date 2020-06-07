import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def hash(data: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)

    return digest.finalize()


def hash_str(data: str) -> bytes:
    return hash(bytes(data, 'utf-8'))


def encrypt(data: bytes, password: str) -> bytes:
    aesgcm = AESGCM(hash_str(password))
    nonce = os.urandom(12)

    ct = aesgcm.encrypt(nonce,  data, None)

    return nonce + ct


def decrypt(data: bytes, password: str) -> bytes:
    aesgcm = AESGCM(hash_str(password))
    nonce = data[0:12]

    ct = aesgcm.decrypt(nonce, data[12::], None)

    return ct
