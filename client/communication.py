import socket
import pickle
from threading import Thread
import time
import os
from path import Path

import chat_refresher
import datamanager
import api_gate

# settings for file stream
import progress_bar
import submit
import upload

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096  # send 4096 bytes each time step

# basic info needed to start the client (ID taken from API), password here is a local key
USER = None
PORT = None
ID = None
PASSWORD = None
HOST = "localhost"
REGISTERED = False


# getting this client's ID from API
def setup_id():
    users = api_gate.get_users_list()
    for user in users:
        if user["name"] == USER:
            global ID
            ID = user["id"]
            return
    print("Could not set user's ID")


# sending text message to target on port where it listens to
def send_text_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            msg = pickle.dumps(message)
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
            # preparing size
            print(filename)
            filesize = os.path.getsize(filename)
            msg = pickle.dumps(message)
            s.send(msg)
            progress_bar.show()
            bytes_sent = 0
            # transferring packets of data to target
            with open(filename, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    s.sendall(bytes_read)
                    bytes_sent += BUFFER_SIZE
                    progress_bar.bar['value'] = (bytes_sent/filesize) * 100
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
            msg = conn.recv(1024)
            data = pickle.loads(msg)

            # listening behavior for upload or text
            if data["type"] == "upload_message":
                print("Transferring upload message..")
                filename = os.path.basename(data["message"])
                filesize = int(data["file_size"])

                # changing path to new path of file
                data["message"] = os.path.abspath(os.path.dirname(__file__))+\
                                  '/downloads/'+os.path.basename(data["message"])
                datamanager.add_upload_message(data["author"], data["author"], data["target_id"],
                                               data["id"], data["message"], data["send_time"], data["file_size"], True)

                progress_bar.show()
                bytes_recv = 0
                with open('downloads/'+filename, "wb") as f:
                    while True:
                        bytes_read = conn.recv(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                        bytes_recv += BUFFER_SIZE
                        progress_bar.bar['value'] = (bytes_recv / filesize) * 100
                    progress_bar.dispose()
                    chat_refresher.refresh_chat()
                upload.UPLOADED = False
                print("File succesfully uploaded.")
            elif data["type"] == "text_message":
                data = pickle.loads(msg)
                datamanager.add_text_message(data["author"], data["author"], data["target_id"],
                                             data["id"], data["message"], data["send_time"], True)
                chat_refresher.refresh_chat()
        except ConnectionError:
            print(f"Connection lost with {adr}")
        except EOFError:
            pass
