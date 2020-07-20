import argparse
import sys
import os

import pickle

from getpass import getpass, getuser

import chest.local_data as local_data
import chest.security as security
from chest.colored import Style, colored
import chest.filesystem as filesystem

from .exceptions.ChestException import ChestException
from .exceptions.InvalidMasterPassword import InvalidMasterPassword
from .exceptions.ValueNotStored import ValueNotStored

from cryptography.exceptions import InvalidTag


class Chest:
    @staticmethod
    def run():
        Chest()

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Securely store data by encrypting it.',
            usage='''chest <subcommand> [<args>]

Available subcommands are:
  init    Initialize your personnal chest
  store   Encrypt and store data
  get     Fetch a previously stored data
  delete  Delete a stored value
  list    List stored names
  prune   Delete all stored values 
  coffee  Brew some coffee
''')

        parser.add_argument('subcommand', help='Subcommand to execute')

        args = parser.parse_args(sys.argv[1:2])

        autorized_subcommands = (
            'init', 'store', 'get', 'delete', 'list', 'prune', 'coffee')

        if args.subcommand in autorized_subcommands:
            code = getattr(self, args.subcommand)()

            if code is not None and type(code) is int and code > 0:
                exit(code)
        else:
            parser.print_help()

    def is_initialized(self) -> bool:
        filepath = local_data.appfile('.m', create=False)
        return filepath.exists()

    def get_masterpwd_hash(self) -> bytes:
        filepath = local_data.appfile('.m', create=False)

        f = open(filepath, 'rb')
        h = f.read()
        f.close()

        return h

    def ask_masterpwd(self) -> bytes:
        h = self.get_masterpwd_hash()

        master = getpass('Enter master password: ')
        sys.stdout.write("\033[F\033[K\r")

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

        if not self.is_initialized():
            print(colored("An initialization is needed.",
                          Style.FAIL), file=sys.stderr)
            return 1

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

            filesystem.store(name, value, master)
            print(
                colored(f"'{name}' has been successfully stored!", Style.OKGREEN))
        except ChestException as e:
            print(colored(e.message, Style.FAIL), file=sys.stderr)
            return 1

    def get(self):
        parser = argparse.ArgumentParser(
            description='Fetch a previously stored data')

        parser.add_argument('name', help="Value's name", type=str)

        args = parser.parse_args(sys.argv[2:])

        if not self.is_initialized():
            print(colored("An initialization is needed.",
                          Style.FAIL), file=sys.stderr)
            return 1

        try:
            master = self.ask_masterpwd()

            value = filesystem.get(args.name, master)
            print(value)
        except ChestException as e:
            print(colored(e.message, Style.FAIL), file=sys.stderr)
            return 1

    def list(self):
        parser = argparse.ArgumentParser(
            description='List stored names')

        parser.add_argument(
            '--hash', help="Display the hashes along with the elements", action="store_true", default=False)

        args = parser.parse_args(sys.argv[2:])

        if not self.is_initialized():
            print(colored("An initialization is needed.",
                          Style.FAIL), file=sys.stderr)
            return 1

        try:
            master = self.ask_masterpwd()

            value = filesystem.get_list(master, args.hash)
            print(value)
        except ChestException as e:
            print(colored(e.message, Style.FAIL), file=sys.stderr)
            return 1

    def delete(self):
        parser = argparse.ArgumentParser(
            description='Delete a stored value')

        parser.add_argument('name', help="Value's name", type=str)

        args = parser.parse_args(sys.argv[2:])

        if not self.is_initialized():
            print(colored("An initialization is needed.",
                          Style.FAIL), file=sys.stderr)
            return 1

        try:
            master = self.ask_masterpwd()

            filesystem.delete(args.name, master)
            print(
                colored(f"'{args.name}' has been successfully deleted!", Style.OKGREEN))
        except ChestException as e:
            print(colored(e.message, Style.FAIL), file=sys.stderr)
            return 1

    def prune(self):
        parser = argparse.ArgumentParser(
            description='Delete all stored values')

        if not self.is_initialized():
            print(colored("An initialization is needed.",
                          Style.FAIL), file=sys.stderr)
            return 1

        try:
            master = self.ask_masterpwd()

            res = input("Delete all your stored files ? [y/N]: ")

            if res.lower() != "y":
                print(colored("You decided to keep your files", Style.WARNING))
                return 1

            for file in os.listdir(local_data.appdir()):
                if (file[0] != "."):
                    local_data.appfile(file).unlink()

            listFile = local_data.appfile(".list")
            if listFile.exists():
                with open(listFile, "w"):
                    pass

            print(colored("Your files are now deleted.", Style.OKGREEN))
        except ChestException as e:
            print(colored(e.message, Style.FAIL), file=sys.stderr)
            return 1

    def coffee(self):
        print(f"""
        Here is your coffee, {getuser()}
    ( (
    ) )
  ........
  |      |]
  \      /
   `----'""")
