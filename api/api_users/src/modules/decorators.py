import os
import json

from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from base64 import b64decode

from flask import Response, request
from functools import wraps

from api_users.src import app


# TODO - Refatorization is needed! It is good idea to split code into separated classes.
#  Especially class responsible for server side encoding and decoding.

def token_authentication_needed(func):

    @wraps(func)
    def function_wrapper(*args, **kwargs):
        token = request.headers.get('token', None)
        if token is None:
            return Response('Invalid token needed to authentication', status=405)

        token = json.loads(token)
        iv = b64decode(token['iv'])
        secret = b64decode(token['secret'])
        login = token['login']

        user_token_file_path = os.path.join(app.config.get('USERS_KEYS_FOLDER_PATH', ''), login, 'secrets.bin')
        server_key_file_path = os.path.join(app.config.get('USERS_KEYS_FOLDER_PATH', ''), 'server', 'key.json')

        if not os.path.exists(user_token_file_path):
            return Response(status=405)

        server_key, server_iv = '', ''
        with open(server_key_file_path, 'r') as file:
            cipher_data = json.loads(file.read())
            server_key = b64decode(cipher_data.get('key', ''))
            server_iv = b64decode(cipher_data.get('iv', ''))

        with open(user_token_file_path, 'rb') as file:
            secrets = file.read()

            descriptor = AES.new(server_key, AES.MODE_CBC, server_iv)
            secrets = unpad(descriptor.decrypt(secrets), AES.block_size).decode('utf-8')
            secrets = json.loads(secrets)

            key = secrets.get('key', '').encode('utf-8')

            cipher = AES.new(key, AES.MODE_CBC, iv)
            secret = unpad(cipher.decrypt(secret), AES.block_size).decode('utf-8')

            if not (secrets['login'] == login and secrets['secret'] == secret):
                return Response(status=405)

        print(f'User with login {login} authenticated successfully')
        return func(*args, **kwargs)

    return function_wrapper
