import pickle

import chest.security as security
import chest.local_data as local_data

from .exceptions.ValueNotStored import ValueNotStored
from .exceptions.InvalidMasterPassword import InvalidMasterPassword

from cryptography.exceptions import InvalidTag


def add_to_list(name: str, hashed: bytes, master: bytes):
    filepath = local_data.appfile(".list")

    if name in get_list(master, False).split('\n'):
        return

    data = filepath.read_bytes()

    if len(data) > 0:
        try:
            data = security.decrypt(data, master)
        except InvalidTag:
            raise InvalidMasterPassword()

        data = pickle.loads(data)

    data += bytes(f"{name}={hashed}\n", 'utf8')

    data = pickle.dumps(data)
    data = security.encrypt(data, master)
    filepath.write_bytes(data)


def get_list(master: bytes, hashes: bool) -> str:
    filepath = local_data.appfile(".list")

    data = filepath.read_bytes()

    if len(data) > 0:
        try:
            data = security.decrypt(data, master)
        except InvalidTag:
            raise InvalidMasterPassword()

        data = pickle.loads(data)

    data = str(data, 'utf8')

    if not hashes:
        data = "\n".join(map(lambda s: s.split("=")[0], data.split("\n")))

    return data


def store(name: str, value: str, master: bytes):
    filename = security.hash_str(name).hex()
    filepath = local_data.appfile(filename)

    data = pickle.dumps(value)
    data = security.encrypt(data, master)

    filepath.write_bytes(data)

    add_to_list(name, filename, master)


def get(name: str, master: bytes) -> str:
    filename = security.hash_str(name).hex()
    filepath = local_data.appfile(filename, create=False)

    if filepath.exists():
        data = filepath.read_bytes()

        try:
            data = security.decrypt(data, master)
        except InvalidTag:
            raise InvalidMasterPassword()

        return pickle.loads(data)
    else:
        raise ValueNotStored(name)


def delete(name: str, master: bytes):
    filename = security.hash_str(name).hex()
    filepath = local_data.appfile(filename, create=False)

    if filepath.exists():
        data = filepath.read_bytes()

        try:
            data = security.decrypt(data, master)
        except InvalidTag:
            raise InvalidMasterPassword()

        filepath.unlink()
    else:
        raise ValueNotStored(name)
