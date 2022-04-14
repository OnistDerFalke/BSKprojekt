from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA512

import cipher
import communication


# generating 16 byte session key
def generate_session_key():
    return get_random_bytes(16)


# encryption of data with session_key given
def cipher_data(data, session_key):
    if cipher.mode == cipher.CipherMode.CBC:
        aes_session_key = AES.new(session_key, AES.MODE_CBC)
    elif cipher.mode == cipher.CipherMode.ECB:
        aes_session_key = AES.new(session_key, AES.MODE_ECB)
    else:
        print("No cipher mode was given.")
        return None, None, None

    ciphertext, tag = aes_session_key.encrypt_and_digest(data)
    nonce = aes_session_key.nonce
    return ciphertext, tag, nonce


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
