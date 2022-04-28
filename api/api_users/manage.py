import json
import os
import sys
from base64 import b64encode

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from src.modules.commands_parser import ManageCommandParser


# TODO - export UserTokenRequester to other file with all needed functions


class UserTokenRequester(object):
    def __init__(self, token_file_path: str):
        self.token_file_path = token_file_path
        self.validate_state()

    def validate_state(self):
        if not os.path.exists(self.token_file_path):
            raise FileNotFoundError(f'Token file was not found in {self.token_file_path}')

    def _get_token_fields(self):
        with open(self.token_file_path, 'r') as file:
            return json.loads(file.read())

    def _prepare_token_request_header(self):
        token = self._get_token_fields()

        login = token.get('login', '')
        secret = token.get('secret', '')
        key = token.get('key', '').encode('utf-8')

        cipher = AES.new(key, AES.MODE_CBC)
        secret_bin = pad(secret.encode('utf-8'), AES.block_size)

        secret_bytes = cipher.encrypt(secret_bin)

        iv = b64encode(cipher.iv).decode('utf-8')
        secret = b64encode(secret_bytes).decode('utf-8')

        return json.dumps({
            'login': login,
            'secret': secret,
            'iv': iv
        })

    def get_all_users(self):
        return requests.get('http://127.0.0.1:8080/api/users', headers={
            'token': self._prepare_token_request_header(),
        })


def main(argv: list[str]):
    commands_parser = ManageCommandParser()
    commands_parser.parse(argv)


if __name__ == "__main__":
    main(sys.argv)
