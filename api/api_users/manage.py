import json
import os
import random
import secrets
import sys
from abc import ABC, abstractmethod
from base64 import b64encode, b64decode

import requests
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad

KEYS_FOLDER_DIR = os.path.join('.', 'src', 'static', 'keys')
SERVER_KEY_FILE_PATH = os.path.join(KEYS_FOLDER_DIR, 'server', 'key.json')

# TODO - Refatorization is needed! It is good idea to split code into separated classes.
#  Especially class responsible for server side encoding and decoding.


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass


class GenerateTokenCommand(Command):
    def execute(self):
        utg = UserTokenGenerator()

        user_login = utg.generate_user_login()
        user_secret = utg.generate_secret()
        key = utg.generate_key()

        # Client side token
        token_secrets_path = os.path.join('.', 'token.json')
        with open(token_secrets_path, 'w') as file:
            file.write(json.dumps({
                'login': user_login,
                'secret': user_secret,
                'key': key
            }))

        # Server side token
        if not os.path.exists(KEYS_FOLDER_DIR):
            os.mkdir(KEYS_FOLDER_DIR)

        token_folder_path = os.path.join(KEYS_FOLDER_DIR, user_login)
        if not os.path.exists(token_folder_path):
            os.mkdir(token_folder_path)

        token_secrets_path = os.path.join(token_folder_path, 'secrets.bin')
        server_side_token = json.dumps({
                'login': user_login,
                'secret': user_secret,
                'key': key
        }).encode('utf-8')

        with open(SERVER_KEY_FILE_PATH, 'r') as file:
            cipher_data = json.loads(file.read())
            key = b64decode(cipher_data['key'])
            iv = b64decode(cipher_data['iv'])

            cipher = AES.new(key, AES.MODE_CBC, iv)
            server_side_token = pad(server_side_token, AES.block_size)
            server_side_token = cipher.encrypt(server_side_token)

        with open(token_secrets_path, 'wb') as file:
            file.write(server_side_token)

        print(f'''
            Yay ^^ Your token has been generated successfully. 
            You can find your token file named "token.json" in
            "{token_secrets_path}" directory. Please placed them 
            in secure environment in your local computer. You will need
            that file to make authenticated requests to the API server.       
        ''')


class UserTokenGenerator(object):

    def __init__(self, random_state=random.random()):
        self.random_state = random_state

    def generate_private_public_keys(self, size: int = 2048) -> tuple[str, str]:
        """ Generate private and public RSA keys pair.

        Parameters
        ----------
        size : int
            Key size (in bits) of the RSA modulus. It must be at least 1024,
            but **2048 is recommended.** The FIPS standard only defines 1024, 2048 and 3072.

        Returns
        -------
        (public, private) : tuple[str, str]
            Pair of public and private RSA keys.

        Raises
        ------
        ValueError
            When type of size argument is different than allowed.
        """
        if not isinstance(size, int):
            raise ValueError(f"Incorrect size argument type. Must be int, not {type(size)}")

        keys = RSA.generate(size)

        public_key = keys.publickey()
        public_key_pem = public_key.exportKey()
        public_key_pem = public_key_pem.decode('ascii')

        private_key_pem = keys.exportKey()
        private_key_pem = private_key_pem.decode('ascii')

        return public_key_pem, private_key_pem

    def generate_secret(self, size: int = 16) -> str:
        """ Generate random hex with provided size.

        Parameters
        ----------
        size : int, Default = 16
            Size in bytes of generated secret.

        Returns
        -------
        secret : str
            Generated secret with provided size.

        Raises
        ------
        ValueError
            When provided size type is different than allowed.
        """
        if not isinstance(size, int):
            raise ValueError(f"Incorrect size argument type. Must be int, not {type(size)}")

        return secrets.token_hex(size)

    def generate_user_login(self, size: int = 16):
        return self.generate_secret(size)

    def generate_key(self, size: int = 16):
        return self.generate_secret(size)


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


def main(argv: list):
    if 'generatetoken' in argv:
        GenerateTokenCommand().execute()

    req = UserTokenRequester(os.path.join('.', 'token.json'))
    r = req.get_all_users()
    print(r.json())


if __name__ == "__main__":
    main(sys.argv)
