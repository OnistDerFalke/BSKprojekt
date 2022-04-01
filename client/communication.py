import socket
import pickle
from threading import Thread
import time

import chat_refresher
import datamanager
import api_gate


# basic info needed to start the client (ID taken from API)
USER = None
PORT = None
ID = None
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
def receive_text_message():
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
    return


# takes data from socket and save with data manager
def receive_from_socket(conn, adr):
    while True:
        try:
            msg = conn.recv(1024)
            data = pickle.loads(msg)
            datamanager.add_text_message(data["author"], data["author"], data["target_id"],
                                         data["id"], data["message"], data["send_time"], True)
            chat_refresher.refresh_chat()
        except ConnectionError:
            print(f"Connection lost with {adr}")
        except EOFError:
            pass
