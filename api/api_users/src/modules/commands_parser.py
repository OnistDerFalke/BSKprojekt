import os
import json

from abc import ABC, abstractmethod
from collections import OrderedDict

from src.modules.server_key_manager import ServerKeyManager
from src.modules.token_generator import UserTokenGenerator


class Command(ABC):
    """ Abstract interface of command """

    @abstractmethod
    def execute(self):
        pass


class GenerateTokenCommand(Command):
    """ Class being child of Command class responsible
        for handling 'generatetoken' command """

    def __init__(self):
        self._users_keys_folder_path = os.path.join(os.path.join(os.path.dirname(__file__),
                                                                 '..', 'static', 'keys'))
        self._create_users_keys_folder()

    def _create_users_keys_folder(self):
        """ Create (if does not exist) folder for users keys files """
        if not os.path.exists(self._users_keys_folder_path):
            os.mkdir(self._users_keys_folder_path)

    def execute(self):
        """ Execute the command """
        user_key, user_login, user_secret = UserTokenGenerator().generate()

        # Client side client token
        client_token_secrets_path = os.path.join('.', 'token.json')
        with open(client_token_secrets_path, 'w') as file:
            file.write(json.dumps({
                'login': user_login,
                'secret': user_secret,
                'key': user_key
            }))

        # Server side client token
        token_folder_path = os.path.join(self._users_keys_folder_path, user_login)
        if not os.path.exists(token_folder_path):
            os.mkdir(token_folder_path)

        token_secrets_path = os.path.join(token_folder_path, 'secrets.bin')
        server_side_token = json.dumps({
            'login': user_login,
            'secret': user_secret,
            'key': user_key
        }).encode('utf-8')

        server_side_token = ServerKeyManager().encrypt(server_side_token)
        with open(token_secrets_path, 'wb') as file:
            file.write(server_side_token)

        print(f'''
            Yay ^^ Your token has been generated successfully. 
            You can find your token file named "token.json" in
            "{client_token_secrets_path}" directory. Please placed them 
            in secure environment in your local computer. You will need
            that file to make authenticated requests to the API server.       
        ''')


class ManageCommandParser(object):
    """ Class responsible for parsing manage.py file commands
        runs from console and running appropriate commands. """

    def __init__(self):
        self._commands = OrderedDict({
            'generatetoken': GenerateTokenCommand()
        })

    def parse(self, commands):
        """ Parse provided list of comments and invoke all parsed commands actions

        Parameters
        ----------
        commands : list[str]
            List of commands to parse.
        """
        for key, command in self._commands.items():
            if key in commands:
                command.execute()
