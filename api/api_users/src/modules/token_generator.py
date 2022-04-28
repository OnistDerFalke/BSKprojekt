import random
import secrets

from abc import ABC, abstractmethod


class TokenGenerator(ABC):
    """ Abstract interface of token generator """

    @abstractmethod
    def generate(self):
        pass


class UserTokenGenerator(TokenGenerator):
    """ Class being child of TokenGenerator class responsible
        for generating user token needed for connection
        authentication with API server. """

    def __init__(self, random_state=random.random()):
        self.random_state = random_state

    def generate(self) -> tuple[str, str, str]:
        """ Generate token fields.

        Returns
        -------
        (key, login, secret) : (bytes, bytes, bytes)
            Tuple of generated token fields.
        """
        key = self._generate_key()
        login = self._generate_login()
        secret = self._generate_secret()

        return key, login, secret

    def _generate_random_string(self, size: int = 16) -> str:
        """ Generate random string with provided size.

        Parameters
        ----------
        size : int, Default = 16
            Size in bytes of generated string.

        Returns
        -------
        secret : str
            Generated string with provided size.

        Raises
        ------
        ValueError
            When provided size type is different than allowed.
        """
        if not isinstance(size, int):
            raise ValueError(f"Incorrect size argument type. Must be int, not {type(size)}")

        return secrets.token_hex(size)

    def _generate_secret(self, size: int = 16) -> str:
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
        return self._generate_random_string(size)

    def _generate_login(self, size: int = 16) -> str:
        """ Generate user token login.

        Returns
        -------
        login : str
            Generated user login.
        """
        return self._generate_random_string(size)

    def _generate_key(self, size: int = 16) -> str:
        """ Generate user token key.

        Returns
        -------
        login : str
            Generated user login.
        """
        return self._generate_random_string(size)
