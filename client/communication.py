import socket
import pickle
from threading import Thread
from datetime import datetime
import time
import os

import chat
import chat_refresher
import cipher
import communication
import datamanager
import api_gate
import key_manager
import progress_bar
import submit
import upload

counter = 0
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1048576  # why not to use whole power :)

# basic info needed to start the client (ID taken from API), password here is a local key
USER = None
PORT = None
ID = None
PASSWORD = None
HOST = "localhost"
REGISTERED = False
PRIVATE = None
PUBLIC = None
BINDED = False

# dictionaries with all info about sessions, public keys etc. with other users
sessions = {}
publics = {}

listening = False


# getting this client's ID from API
def setup_id():
    users = api_gate.get_users_list()
    for user in users:
        if user["name"] == USER:
            global ID
            ID = user["id"]
            return
    print("Could not set user's ID")


# sending acknowledgement to inform that message has been received
def send_acknowledgement(host, port, target_id, user):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            global PUBLIC, USER, PORT
            message_data = {
                "type": "text_message",
                "message": "YOUR MESSAGE HAS BEEN RECEIVED",
                "author": USER,
                "send_time": datetime.now().strftime("%H:%M"),
                "is_external": True,
                "id": ID,
                "target_id": target_id,
                "is_sent": True,
                "acknowledgement": True
            }

            message = key_manager.cipher_data(pickle.dumps(message_data),
                                              sessions[user]["session_key"],
                                              sessions[user]["iv"],
                                              sessions[user]["aes_mode"])
            msg_pkg = {
                "pkg": "message",
                "author": USER,
                "msg": message
            }
            msg = pickle.dumps(msg_pkg)
            msg = msg.rjust(65536, b'0')
            s.send(msg)
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
    return


# sending session key to target on port where it listens to
def send_session_key(host, port):
    while not (chat_refresher.ACTIVE_USERNAME in publics):
        time.sleep(0.1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            session_key = key_manager.generate_session_key()
            iv = key_manager.generate_iv()
            my_msg = {
                "pkg": "session_key",
                "aes_mode": cipher.mode,
                "session_key": session_key,
                "iv": iv,
                "author": chat_refresher.ACTIVE_USERNAME
            }
            sessions[chat_refresher.ACTIVE_USERNAME] = my_msg
            msg = my_msg.copy()
            msg["author"] = USER
            msg["session_key"] = key_manager.encrypt_with_rsa_key(publics[chat_refresher.ACTIVE_USERNAME]["public_key"],
                                                                  session_key)
            msg["iv"] = key_manager.encrypt_with_rsa_key(publics[chat_refresher.ACTIVE_USERNAME]["public_key"],
                                                         iv)
            msg = pickle.dumps(msg)
            msg = msg.rjust(65536, b'0')
            s.send(msg)
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
    return


# sending public key to target on port where it listens to
def send_public_key(host, port, is_exchanged):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            global PUBLIC, USER, PORT
            msg_pkg = {
                "pkg": "public_key",
                "public_key": PUBLIC,
                "author": USER,
                "is_exchanged": is_exchanged,
                "port": PORT
            }
            msg = pickle.dumps(msg_pkg)
            msg = msg.rjust(65536, b'0')
            s.send(msg)
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
    return


# sending text message to target on port where it listens to
def send_text_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))

            # ciphering message and sending as element of a kind of "frame"
            message = key_manager.cipher_data(pickle.dumps(message),
                                              sessions[chat_refresher.ACTIVE_USERNAME]["session_key"],
                                              sessions[chat_refresher.ACTIVE_USERNAME]["iv"],
                                              sessions[chat_refresher.ACTIVE_USERNAME]["aes_mode"])
            message_pkg = {
                "pkg": "message",
                "msg": message,
                "author": USER
            }
            msg = pickle.dumps(message_pkg)
            msg = msg.rjust(65536, b'0')
            s.send(msg)
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
    return


# sending upload message to target on port where it listens to
def send_upload_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            filename = message["message"]

            # encrypting the file and saving to temp file
            with open(filename, "rb") as f:
                with open("temp/ciphered.txt", "wb") as t:
                    encrypted_bytes = f.read()
                    encrypted_bytes = key_manager.cipher_data(pickle.dumps(encrypted_bytes),
                                                              sessions[chat_refresher.ACTIVE_USERNAME]["session_key"],
                                                              sessions[chat_refresher.ACTIVE_USERNAME]["iv"],
                                                              sessions[chat_refresher.ACTIVE_USERNAME]["aes_mode"])
                    t.write(encrypted_bytes)
                    t.close()

            # file size has been set
            message["file_size_encrypted"] = os.path.getsize("temp/ciphered.txt")

            # ciphering message with info about the file and sending as a part of "frame"
            message = key_manager.cipher_data(pickle.dumps(message),
                                              sessions[chat_refresher.ACTIVE_USERNAME]["session_key"],
                                              sessions[chat_refresher.ACTIVE_USERNAME]["iv"],
                                              sessions[chat_refresher.ACTIVE_USERNAME]["aes_mode"])
            message_pkg = {
                "pkg": "message",
                "msg": message,
                "author": USER
            }
            msg = pickle.dumps(message_pkg)
            msg = msg.rjust(65536, b'0')
            s.send(msg)

            # initializing the sending progress bar
            progress_bar.init()
            progress_bar.show()
            bytes_sent = 0

            # transferring packets of data to target
            with open("temp/ciphered.txt", "rb") as f:
                filesize = os.path.getsize("temp/ciphered.txt")
                while bytes_sent < filesize:
                    bytes_read = f.read(BUFFER_SIZE)
                    s.sendall(bytes_read)
                    bytes_sent += len(bytes_read)
                    progress_bar.bar['value'] = (bytes_sent / filesize) * 100
                progress_bar.dispose()
                submit.filePath.set("")
                submit.file = None
                upload.UPLOADED = False
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
    return


# verifying connection on port where target is listening
def verify_connection(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
            return False
    return True


# listening to incoming messages
def receive_message():
    # unregistered user cannot listen
    while not REGISTERED:
        time.sleep(1)

    # registering user in api
    api_gate.reg_user_in_api(USER, PORT)

    # setting ID from api
    if ID is None:
        setup_id()
        print(f'Current user ID is now: {ID}')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        BINDED = True
        s.listen()
        print("Waiting for connection accept..")
        while BINDED:
            print(f"Listening on {HOST}:{PORT}")
            conn, adr = s.accept()
            print("Connection accepted.")
            Thread(target=receive_from_socket, args=(conn, adr,)).start()
        s.close()


# takes data from socket and save with data manager
def receive_from_socket(conn, adr):
    global listening
    fake_session = key_manager.generate_session_key();
    while True:
        try:
            # getting the frame of any type
            msg = conn.recv(65536)
            if len(msg) > 0:
                msg = msg.lstrip(b'0')
            data = pickle.loads(msg)

            # handle public key frame
            if data["pkg"] == "public_key":
                publics[data["author"]] = data
                if not data["is_exchanged"]:
                    key_manager.exchange_public_with_target(data['author'], data["port"], True)
                return

            # handle session key frame
            if data["pkg"] == "session_key":
                global PRIVATE
                data["session_key"] = key_manager.decrypt_with_rsa_key(PRIVATE, data["session_key"])
                data["iv"] = key_manager.decrypt_with_rsa_key(PRIVATE, data["iv"])
                sessions[data["author"]] = data
                return

            # deciphering data
            if listening:
                tempdata = data.copy()
                data = key_manager.decipher_data(data["msg"], sessions[data["author"]]["session_key"],
                                             sessions[data["author"]]["aes_mode"], sessions[data["author"]]["iv"])
                bad_data = key_manager.decipher_data(tempdata["msg"], fake_session,
                                                 sessions[tempdata["author"]]["aes_mode"], sessions[tempdata["author"]]["iv"])
                datamanager.add_text_message(tempdata["author"], tempdata["author"], 0,
                                             0, bad_data, datetime.now().strftime("%H:%M"), True)
                chat_refresher.refresh_chat()
            else:
                data = key_manager.decipher_data(data["msg"], sessions[data["author"]]["session_key"],
                                             sessions[data["author"]]["aes_mode"], sessions[data["author"]]["iv"])
            data = pickle.loads(data)

            users = api_gate.get_users_list()
            port = None
            if not data["acknowledgement"]:
                for user in users:
                    if user["name"] == data["author"]:
                        port = user["port"]
                        break
                if port is not None:
                    send_acknowledgement("localhost", port, data["target_id"], user["name"])

            # listening behavior for upload or text
            if data["type"] == "upload_message":
                print("Transferring upload message..")
                filename = os.path.basename(data["message"])
                filesize = int(data["file_size_encrypted"])
                filesize_org = int(data["file_size"])

                if not os.path.exists('downloads'):
                    os.makedirs('downloads')

                # changing path to new path of file
                data["message"] = os.path.abspath(os.path.dirname(__file__)) + \
                                  '/downloads/' + os.path.basename(data["message"])

                if not listening:
                    datamanager.add_upload_message(data["author"], data["author"], data["target_id"],
                                               data["id"], data["message"], data["send_time"], data["file_size"], True)

                # setting progress bar for receiving
                if chat.ACTIVE_CHAT == data["author"]:
                    progress_bar.init()
                    progress_bar.show()
                bytes_recv = 0

                # receiving ciphered file
                with open('downloads/' + filename, "wb") as t:
                    content = b''
                    while bytes_recv < filesize:
                        if filesize - bytes_recv < BUFFER_SIZE:
                            bytes_read = conn.recv(filesize - bytes_recv)
                        else:
                            bytes_read = conn.recv(BUFFER_SIZE)
                        content += bytes_read
                        bytes_recv += len(bytes_read)

                        if chat.ACTIVE_CHAT == data["author"]:
                            progress_bar.bar['value'] = (bytes_recv / filesize) * 100

                    # deciphering the whole file after collecting all packages
                    content = key_manager.decipher_data(content, sessions[data["author"]]["session_key"],
                                                        sessions[data["author"]]["aes_mode"],
                                                        sessions[data["author"]]["iv"])
                    if not listening:
                        t.write(pickle.loads(content))
                    progress_bar.dispose()
                    chat_refresher.refresh_chat()
                upload.UPLOADED = False
                print("File succesfully uploaded.")
            elif data["type"] == "text_message":
                if not listening:
                    datamanager.add_text_message(data["author"], data["author"], data["target_id"],
                                                 data["id"], data["message"], data["send_time"], True)
                    chat_refresher.refresh_chat()
        except ConnectionError:
            print(f"Connection lost with {adr}")
        except EOFError:
            pass
