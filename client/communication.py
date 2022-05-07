import socket
import pickle
from threading import Thread
import time
import os

import chat
import chat_refresher
import cipher
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

# dictionary with all info about sessions with other users
sessions = {}


# getting this client's ID from API
def setup_id():
    users = api_gate.get_users_list()
    for user in users:
        if user["name"] == USER:
            global ID
            ID = user["id"]
            return
    print("Could not set user's ID")


# sending session key to target on port where it listens to
def send_session_key(host, port):
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
            msg = pickle.dumps(msg)
            msg = msg.rjust(65536, b'0')
            s.send(msg)
            print(f"Session key has been send on {host}:{port}.")
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
            print(f"Message has been send on {host}:{port}.")
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
        s.listen()
        print("Waiting for connection accept..")
        while True:
            print(f"Listening on {HOST}:{PORT}")
            conn, adr = s.accept()
            print("Connection accepted.")
            Thread(target=receive_from_socket, args=(conn, adr,)).start()


# takes data from socket and save with data manager
def receive_from_socket(conn, adr):
    while True:
        try:
            # getting the frame of any type
            msg = conn.recv(65536)
            if len(msg) > 0:
                msg = msg.lstrip(b'0')
            data = pickle.loads(msg)

            # handle session key frame
            if data["pkg"] == "session_key":
                sessions[data["author"]] = data
                print(f"Session key of user: {data['author']} has been added to dictionary.")
                return

            # deciphering data
            data = key_manager.decipher_data(data["msg"], sessions[data["author"]]["session_key"],
                                             sessions[data["author"]]["aes_mode"], sessions[data["author"]]["iv"])
            data = pickle.loads(data)

            # listening behavior for upload or text
            if data["type"] == "upload_message":
                print("Transferring upload message..")
                filename = os.path.basename(data["message"])
                filesize = int(data["file_size_encrypted"])
                filesize_org = int(data["file_size"])
                # changing path to new path of file
                data["message"] = os.path.abspath(os.path.dirname(__file__)) + \
                                  '/downloads/' + os.path.basename(data["message"])
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
                    t.write(pickle.loads(content))
                    progress_bar.dispose()
                    chat_refresher.refresh_chat()
                upload.UPLOADED = False
                print("File succesfully uploaded.")
            elif data["type"] == "text_message":
                datamanager.add_text_message(data["author"], data["author"], data["target_id"],
                                             data["id"], data["message"], data["send_time"], True)
                chat_refresher.refresh_chat()
        except ConnectionError:
            print(f"Connection lost with {adr}")
        except EOFError:
            pass
