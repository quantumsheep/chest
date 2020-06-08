import argparse
import sys

import pickle

from getpass import getpass

import chest.local_data as local_data
import chest.security as security
from chest.colored import Style, colored

from .exceptions.InvalidMasterPassword import InvalidMasterPassword
from .exceptions.InitializationNeeded import InitializationNeeded

from cryptography.exceptions import InvalidTag


class Chest:
    @staticmethod
    def run():
        Chest()

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Securely store data by encrypting it.',
            usage='''chest <command> [<args>]

Available commands are:
  store  Encrypt and store data
  get    Fetch a previously stored data
''')

        parser.add_argument('subcommand', help='Subcommand to execute')

        args = parser.parse_args(sys.argv[1:2])

        if hasattr(self, args.subcommand):
            code = getattr(self, args.subcommand)()

            if code is not None and type(code) is int and code > 0:
                exit(code)
        else:
            parser.print_help()

    def __get_masterpwd_hash(self) -> bytes:
        filepath = local_data.appfile('.m', create=False)

        if filepath.exists():
            f = open(filepath, 'rb')
            h = f.read()
            f.close()

            return h

        raise InitializationNeeded()

    def ask_masterpwd(self) -> bytes:
        h = self.__get_masterpwd_hash()

        master = getpass('Enter master password: ')
        master_h = security.hash_str(master)

        if master_h != h:
            raise InvalidMasterPassword()

        return master_h

    def init(self):
        masterpath = local_data.appfile('.m', create=False)

        if masterpath.exists():
            print(colored("Initialization has already been done.",
                          Style.FAIL), file=sys.stderr)
        else:
            master = getpass('Enter master password: ')
            master_check = getpass('Re-enter master password: ')

            if master != master_check:
                print(colored("Passwords doesn't match.",
                              Style.FAIL), file=sys.stderr)

                return 1
            else:
                master_h = security.hash_str(master)

                masterpath.write_bytes(master_h)

    def store(self):
        parser = argparse.ArgumentParser(
            description='Encrypt and store data')

        parser.add_argument('-f', '--file', help='File data', type=str)

        args = parser.parse_args(sys.argv[2:])

        name = input("Enter value's name: ")

        value: str = None

        if args.file is not None:
            f = open(args.file, 'rb')
            value = str(f.read(), 'unicode_escape')

            f.close()
        else:
            value = input("Enter value: ")

        try:
            master = self.ask_masterpwd()
        except (InvalidMasterPassword, InitializationNeeded) as e:
            print(e.message, file=sys.stderr)
            return 1

        filename = security.hash_str(name).hex()
        filepath = local_data.appfile(filename)

        data = pickle.dumps(value)
        data = security.encrypt(data, master)

        f = open(filepath, 'wb')
        f.write(data)
        f.close()

    def get(self):
        parser = argparse.ArgumentParser(
            description='Get a stored value')

        parser.add_argument('name', help="Value's name", type=str)

        args = parser.parse_args(sys.argv[2:])

        filename = security.hash_str(args.name).hex()
        filepath = local_data.appfile(filename, create=False)

        if filepath.exists():
            try:
                master = self.ask_masterpwd()
            except (InvalidMasterPassword, InitializationNeeded) as e:
                print(colored(e.message, Style.FAIL), file=sys.stderr)
                return 1

            data = filepath.read_bytes()

            try:
                data = security.decrypt(data, master)
            except InvalidTag:
                print(colored(
                    "Given password does not match the value's password.", Style.FAIL), file=sys.stderr)
                return 1

            data = pickle.loads(data)

            print(data)
        else:
            print(colored(
                f"No value named '{args.name}' is currently stored.", Style.FAIL), file=sys.stderr)
