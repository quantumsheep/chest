import argparse
import sys

import pickle

from getpass import getpass

import chest.local_data as local_data
import chest.security as security

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
            getattr(self, args.subcommand)()
        else:
            parser.print_help()

    def store(self):
        parser = argparse.ArgumentParser(
            description='Encrypt and store data')

        parser.add_argument('-f', '--file', help='File data', type=str)

        args = parser.parse_args(sys.argv[2:])

        name = input("Enter value's name: ")

        value: str = None

        if args.file is not None:
            f = open(args.file, 'rb')
            value = f.read()

            f.close()
        else:
            value = input("Enter value: ")

        master = getpass('Enter master password: ')

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
            master = getpass('Enter master password: ')

            data = filepath.read_bytes()

            try:
                data = security.decrypt(data, master)
            except InvalidTag:
                print("Given password does not match the value's password.")
                return 1

            data = pickle.loads(data)

            print(data)
        else:
            print(
                f"No value named '{args.name}' is currently stored.", file=sys.stderr)
