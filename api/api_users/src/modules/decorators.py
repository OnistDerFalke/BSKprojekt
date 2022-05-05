import os
import json

from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from base64 import b64decode

from flask import Response, request
from functools import wraps

from api_users.src import app
from api_users.src.modules.server_key_manager import ServerKeyManager


def token_authentication_needed(func):

    @wraps(func)
    def function_wrapper(*args, **kwargs):
        token = request.headers.get('token', None)
        if token is None:
            return Response('Invalid token needed to authentication', status=405)

        # unpack header content contains needed fields
        token = json.loads(token)
        iv = b64decode(token['iv'])
        secret = b64decode(token['secret'])
        login = token['login']

        user_token_file_path = os.path.join(app.config.get('USERS_KEYS_FOLDER_PATH', ''),
                                            login, 'secrets.bin')

        if not os.path.exists(user_token_file_path):
            return Response(status=405)

        # Compare header token fields with token fields stores on server side.
        # However to compare that fields it is needed to decrypt server side
        # encrypted client token.
        with open(user_token_file_path, 'rb') as file:
            secrets = file.read()
            secrets = ServerKeyManager().decrypt(secrets).decode('utf-8')
            secrets = json.loads(secrets)

            key = secrets.get('key', '').encode('utf-8')

            cipher = AES.new(key, AES.MODE_CBC, iv)
            secret = unpad(cipher.decrypt(secret), AES.block_size).decode('utf-8')

            if not (secrets['login'] == login and secrets['secret'] == secret):
                return Response(status=405)

        print(f'User with login {login} was authenticated successfully')
        return func(*args, **kwargs)

    return function_wrapper
