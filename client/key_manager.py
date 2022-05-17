import json
import os.path
import secrets
import base64
import random
import string
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA3_256
from Crypto.Random import get_random_bytes
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
    try:
        if mode == cipher.CipherMode.CBC:
            aes_session_key = AES.new(session_key, AES.MODE_CBC, iv)
            return unpad(aes_session_key.decrypt(data), AES.block_size)
        elif mode == cipher.CipherMode.ECB:
            aes_session_key = AES.new(session_key, AES.MODE_ECB)
            return unpad(aes_session_key.decrypt(data), AES.block_size)
        print("Decipher mode was not given or it is incorrect.")
        return
    except ValueError:
        val = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
        return val



# RSA encryption of session key with second user's RSA public key
def cipher_session_key(session_key, receiver_key):
    cipher_rsa = PKCS1_OAEP.new(receiver_key)
    return cipher_rsa.encrypt(session_key)


# hash user-friendly password
def hash_password(password):
    hashed = SHA3_256.new()
    hashed.update(password.encode(encoding='utf-8'))
    return hashed.digest()


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

    to_str : bool, Optional. Default = False.
        Should returned encrypted message be converted to string.

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


def save_key_with_password(key: Union[bytes, str], password: Union[bytes, str], out_folder_path: str):
    """ Save password and key in folder in provided path.

    Parameters
    ----------
    key : Union[str, bytes]
        Key to save.

    password : Union[str, bytes]
        Password for saved file.

    out_folder_path : str
        Path to the folder where files should be saved.
    """
    content = json.dumps({
        'key': key if isinstance(key, str) else key.decode('utf-8'),
        'password': password if isinstance(password, str) else base64.b64encode(password).decode('utf-8')
    }).encode('utf-8')

    if isinstance(password, str):
        password = password.encode('utf-8')

    aes = AES.new(password, AES.MODE_CBC)
    encrypted_content = pad(content, AES.block_size)
    encrypted_content = aes.encrypt(encrypted_content)

    if not os.path.exists(out_folder_path):
        os.mkdir(out_folder_path)

    iv_path = os.path.join(out_folder_path, 'iv.bin')
    with open(iv_path, 'wb') as file:
        file.write(aes.iv)

    content_path = os.path.join(out_folder_path, 'secrets.bin')
    with open(content_path, 'wb') as file:
        file.write(encrypted_content)


def extract_key_with_password(password: Union[str, bytes], from_folder_path: str, to_str: bool = False):
    """ Extract key from encrypted file using provided password.

    Parameters
    ----------
    password : Union[str, bytes]
        Password to the files.

    from_folder_path : str
        Path to folder with encrypted files.

    to_str : bool, Optional. Default = False.
        Should extracted key be converted to string.

    Returns
    -------
    key : Union[None, bytes, str].
        If password was incorrect None is returned.
        Otherwise bytes or str depending on the value of parameter `to_str`.
    """
    key = password if isinstance(password, bytes) else password.encode('utf-8')

    iv_path = os.path.join(from_folder_path, 'iv.bin')
    with open(iv_path, 'rb') as file:
        iv = file.read()

    aes = AES.new(key, AES.MODE_CBC, iv)

    # Extract encrypted file content. If key of cipher is
    # different that used for encryption it will throw a
    # ValueError of unpadding
    content_path = os.path.join(from_folder_path, 'secrets.bin')
    with open(content_path, 'rb') as file:
        try:
            decrypted_content = aes.decrypt(file.read())
            decrypted_content = unpad(decrypted_content, AES.block_size)
            decrypted_content = decrypted_content.decode('utf-8')
        except ValueError as e:
            return None

    # If In some case unpadding will be correct could not
    # be possible to create dictionary from extracted content
    try:
        json_content = json.loads(decrypted_content)
    except json.decoder.JSONDecodeError as e:
        return None

    content_pass = json_content.get('password', '')

    if isinstance(password, bytes):
        password = base64.b64encode(password).decode('utf-8')

    if content_pass != password:
        return None

    # If (in chance 1 to inf) dictionary could be created
    # dictionary key of encrypted key should not exist
    extracted_key = json_content.get('key', None)
    if not to_str and extracted_key is not None:
        return extracted_key.encode('utf-8')

    return extracted_key


if __name__ == '__main__':
    key = b'---- PUBLIC RSA KEY ------ XDASDKASHDAXDAHSKDASHDKASDKASHDKASHDKAS -- END OF KEY --'
    password = secrets.token_hex(16)
    out_folder_path = '.\\ExampleUsername'

    save_key_with_password(key, password, out_folder_path)
    extracted_key = extract_key_with_password(password, out_folder_path, to_str=True)
    print(extracted_key)

    extracted_key = extract_key_with_password(secrets.token_hex(16), out_folder_path)
    print(extracted_key)
