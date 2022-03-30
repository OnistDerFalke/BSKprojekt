from datetime import datetime

import communication
import datamanager
from threading import Thread

import chat_refresher

file = None
filePath = None


def send_message(name, message, id, target):
    text_message = message
    send_time = datetime.now().strftime("%H:%M")
    final_message = datamanager.add_text_message("Me", target.name, id, target.id, text_message, send_time, False,
                                                 communication.verify_connection(target.host, target.port))
    final_message["author"] = name
    send_message_thread = Thread(target=communication.send_text_message,
                                 args=(target.host, target.port, final_message,))
    send_message_thread.start()
    chat_refresher.refresh_chat()
    return
