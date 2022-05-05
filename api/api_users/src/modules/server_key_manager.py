import os
import json

from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class ServerKey(object):
    """ Class represents server key object contains
        fields needed to decrypt or encrypt bytes data using that key.
    """

    def __init__(self, path):
        self._path = path
        self._key, self._iv = self._load_key_iv()
        self.validate_state()

    def _load_key_iv(self):
        """ Load key and iv vector from file
        to which path was provided in object creation.
        """
        with open(self._path, 'r') as file:
            key_content = json.loads(file.read())
            key = b64decode(key_content.get('key', ''))
            iv = b64decode(key_content.get('iv', ''))
            return key, iv

    def validate_state(self):
        """ Validate state of the object after
        all variables initialization. """
        if not os.path.exists(self._path):
            raise FileNotFoundError(f'Key file does not exist in path {self._path}')

        if self._key == b'' or self._iv == b'':
            raise ValueError('Incorrect value of "key" attribute in server key file')

    @property
    def key(self):
        return self._key

    @property
    def iv(self):
        return self._iv


class ServerKeyManager(object):
    """ Class represents server key manager
        that provides useful functions related to server key management
    """

    def __init__(self):
        self._server_key = ServerKey(os.path.join(os.path.dirname(__file__),
                                                  '..', 'static', 'keys', 'server', 'key.json'))
        self._cipher = AES.new(self._server_key.key, AES.MODE_CBC, self._server_key.iv)

    def encrypt(self, data: bytes) -> bytes:
        """ Encrypt provided data,

        Parameters
        ----------
        data : bytes
            Data to encrypt.

        Returns
        -------
        encrypted_data : bytes
            Encrypted provided data.
        """
        if not isinstance(data, bytes):
            raise ValueError(f'Invalid type of input data parameter. Could not be {type(data)}')

        encrypted_data = pad(data, AES.block_size)
        encrypted_data = self._cipher.encrypt(encrypted_data)
        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        """ Decrypt provided data.

        Parameters
        ----------
        data : bytes
            Data to decrypt.

        Returns
        -------
        decrypted_data : bytes
            Decrypted provided data.
        """
        if not isinstance(data, bytes):
            raise ValueError(f'Invalid type of input data parameter. Could not be {type(data)}')

        decrypted_data = self._cipher.decrypt(data)
        decrypted_data = unpad(decrypted_data, AES.block_size)
        return decrypted_data

    @property
    def server_key(self):
        return self._server_key
