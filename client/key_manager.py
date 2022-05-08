from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA512
from Crypto.Util.Padding import pad, unpad
from threading import Thread
from typing import Union
import base64

import cipher
import communication


# generating 16 byte session key
def generate_session_key():
    return get_random_bytes(16)


# generating iv
def generate_iv():
    return get_random_bytes(AES.block_size)


# encryption of data with session_key given
def cipher_data(data, session_key, iv, mode):
    if mode == cipher.CipherMode.CBC:
        aes_session_key = AES.new(session_key, AES.MODE_CBC, iv)
        return aes_session_key.encrypt(pad(data, AES.block_size))
    elif mode == cipher.CipherMode.ECB:
        aes_session_key = AES.new(session_key, AES.MODE_ECB)
        return aes_session_key.encrypt(pad(data, AES.block_size))
    print("Cipher mode was not given or it is incorrect.")
    return


# decryption of data with session_key given
def decipher_data(data, session_key, mode, iv=None):
    if mode == cipher.CipherMode.CBC:
        aes_session_key = AES.new(session_key, AES.MODE_CBC, iv)
        return unpad(aes_session_key.decrypt(data), AES.block_size)
    elif mode == cipher.CipherMode.ECB:
        aes_session_key = AES.new(session_key, AES.MODE_ECB)
        return unpad(aes_session_key.decrypt(data), AES.block_size)
    print("Decipher mode was not given or it is incorrect.")
    return


# RSA encryption of session key with second user's RSA public key
def cipher_session_key(session_key, receiver_key):
    cipher_rsa = PKCS1_OAEP.new(receiver_key)
    return cipher_rsa.encrypt(session_key)


# hash user-friendly password
def hash_password(password):
    hashed = SHA512.new()
    hashed.update(bytes(password, 'utf-8'))
    return hashed


# cipher the rsa key with local key
def encrypt_rsa_key(rsa_key):
    aes_key = AES.new(communication.PASSWORD, AES.MODE_CBC)
    ciphertext, tag = aes_key.encrypt_and_digest(rsa_key)
    nonce = aes_key.nonce
    return ciphertext, tag, nonce


# exchanging session key (sending session key frame)
def exchange_key_with_target(target, port):
    if not (target in communication.sessions):
        key_exchange_thread = Thread(target=communication.send_session_key,
                                     args=("localhost", port))
        key_exchange_thread.start()


# exchanging public key (sending session key frame)
def exchange_public_with_target(target, port, is_exchanged):
        public_exchange_thread = Thread(target=communication.send_public_key,
                                        args=("localhost", port, is_exchanged))
        public_exchange_thread.start()


def generate_rsa_keys(size: int = 2048):
    """ Generate public and private RSA keys with provided size.

    Parameters
    ----------
    size : int Optional. Default=2048.
        Optional size in bytes of RSA key.

    Returns
    -------
    (private, public) : Tuple[bytes, bytes]
        Generated tuple of private and public keys.
    """
    key = RSA.generate(size)
    pub_key = key.publickey()
    return key.export_key(), pub_key.export_key()


def encrypt_with_rsa_key(key: bytes, message: Union[bytes, str], to_str=False):
    """ Encrypt provided message using provided RSA key.

    Parameters
    ----------
    key : bytes
        Key using in encryption.

    message : Union[bytes, str]
        Message to encrypt.

    Returns
    -------
    message : bytes
        Encrypted message.
    """
    if isinstance(message, str):
        message = message.encode('utf-8')

    rsa_key = RSA.import_key(key)

    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_msg = cipher.encrypt(message)
    encrypted_msg = base64.b64encode(encrypted_msg)

    if to_str:
        encrypted_msg = encrypted_msg.decode('utf-8')

    return encrypted_msg


def decrypt_with_rsa_key(key: bytes, message: Union[bytes, str], to_str=False):
    """ Decrypt provided message using provided RSA key.

    Parameters
    ----------
    key : bytes
        Key using in encryption.

    message : Union[bytes, str]
        Message to encrypt.

    to_str : bool, Optional. Default = False.
        Should returned message be converted to string.

    Returns
    -------
    message : bytes
        Decrypted message.
    """
    if isinstance(message, str):
        message = message.encode('utf-8')

    rsa_key = RSA.import_key(key)

    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_msg = base64.b64decode(message)
    decrypted_msg = cipher.decrypt(encrypted_msg)

    if to_str:
        decrypted_msg = decrypted_msg.decode('utf-8')

    return decrypted_msg
