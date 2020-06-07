import argparse
import sys

import pickle

from getpass import getpass

import chest.local_data as local_data
import chest.security as security


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
        value = input("Enter value: ")
        master = getpass('Enter master password: ')

        filename = security.hash_str(name).hex()
        values_path = local_data.appfile(filename)

        content = values_path.read_bytes()

        data = pickle.dumps(value)
        data = security.encrypt(data, master)

        f = open(values_path, 'wb')
        f.write(data)
