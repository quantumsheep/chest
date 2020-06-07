from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


def hash(data: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)

    return digest.finalize()
