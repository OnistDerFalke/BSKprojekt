import json
import os
from base64 import b64encode

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class UserTokenizedRequester(object):
    """ Class needed to proper authentication on API server.
    Token file has to be generated before use that class.
    """

    def __init__(self, token_file_path: str, base_url: str):
        """ Initialize UserTokenizedRequest object with provided attributes.

        Parameters
        ----------
        token_file_path : str
            Path to the token file.

        base_url : str
            Base URL to server API with '/' sign at the end.
        """
        self.token_file_path = token_file_path
        self.base_url = base_url
        self._validate_state()

    def _validate_state(self):
        """ Validate state of initialized object. """
        if not os.path.exists(self.token_file_path):
            raise FileNotFoundError(f'Token file was not found in {self.token_file_path}')

        if self.base_url[-1] != '/':
            raise AttributeError('Incorrect base url. Last sign has to be "/"')

        try:
            requests.get(self.base_url)
        except ConnectionError:
            raise ConnectionError(f'Server with url = {self.base_url} is unreachable')

    def _get_token_dict(self):
        """ Returns transformed to dict loaded token fields.

        Returns
        -------
        token : dict
            Loaded token dictionary.
        """
        with open(self.token_file_path, 'r') as file:
            return json.loads(file.read())

    def _prepare_token_request_header(self):
        """ Prepare header token for sending it in request.

        Returns
        -------
        token : str
            Prepared token string.
        """
        token = self._get_token_dict()

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

    def _parse_response(self, response: requests.Response, failed_value=None):
        """ Parse response from server.

        Parameters
        ----------
        response : Response
            Response object to parse.

        failed_value : any
            Value returned when response status is different than success.
        """
        if response.status_code == 405:
            raise ConnectionError('Method is not allowed. Check user token corectness.')
        if response.status_code != 200:
            return failed_value
        else:
            return response.json()

    def get_users_list(self):
        """ Get list of all exising users from API server.

        Returns
        -------
        users : list
            Responded users list.
        """
        try:
            response = requests.get(f'{self.base_url}api/users', headers={
                'token': self._prepare_token_request_header()
            })
            return self._parse_response(response, failed_value=[])
        except ConnectionError as error:
            print(error)

    def reg_user(self, username: str, port: int):
        """ Register user with provided port and username on API server.

        Parameters
        ----------
        username : str
            Username of user.

        port : int
            Port of user.
        """
        try:
            response = requests.post(f'{self.base_url}api/users', json={
                "name": username,
                "port": port
            }, headers={
                'token': self._prepare_token_request_header()
            })
            print(f"User register with status code: {response.status_code}")
            return self._parse_response(response)
        except ConnectionError as error:
            print(error)

    def unreg_user(self, username: str, port: int):
        """ Unregister user with provided port and username from API server.

        Parameters
        ----------
        username : str
            Username of user.

        port : int
            Port of user.
        """
        user_to_delete = None
        users = self.get_users_list()
        for user in users:
            if user["name"] == username and user["port"] == port:
                user_to_delete = user
                break

        if user_to_delete is None:
            return

        try:
            response = requests.delete(f'{self.base_url}api/users/{user_to_delete["id"]}', headers={
                'token': self._prepare_token_request_header()
            })
            print(f"User successfully unregistered with status: {response.status_code}")
            return self._parse_response(response)
        except ConnectionError as error:
            print(error)


if __name__ == "__main__":
    token_path = os.path.join('.', 'token.json')
    utr = UserTokenizedRequester(token_path, 'http://127.0.0.1:8080/')

    print(utr.reg_user('user', 12345))
    print(utr.get_users_list())
    print(utr.unreg_user('user', 12345))
    print(utr.get_users_list())
