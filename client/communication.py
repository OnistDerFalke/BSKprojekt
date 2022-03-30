import socket
import pickle
from threading import Thread

import chat_refresher
import datamanager

HEADERSIZE = 10


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


def verify_connection(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
            return False
    return True


def receive_text_message(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Waiting for connection accept..")
        while True:
            print(f"Listening on {host}:{port}")
            conn, adr = s.accept()
            print("Connection accepted.")
            Thread(target=receive_from_socket, args=(conn, adr,)).start()
    return


def receive_from_socket(conn, adr):
    while True:
        try:
            msg = conn.recv(1024)
            data = pickle.loads(msg)
            datamanager.add_text_message(data["author"], data["author"], data["target_id"], data["id"], data["message"], data["send_time"], True)
            chat_refresher.refresh_chat()
        except ConnectionError:
            print(f"Connection lost with {adr}")
        except EOFError:
            pass
    return
