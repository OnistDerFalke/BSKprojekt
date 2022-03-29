from datetime import datetime

import communication
import datamanager
from threading import Thread

file = None
filePath = None


def send_message(message, name, id, target):
    text_message = message
    send_time = datetime.now().strftime("%H:%M")
    final_message = datamanager.add_text_message(name, id, text_message, send_time)
    send_message_thread = Thread(target=communication.send_text_message,
                                 args=(target.host, target.port, final_message,))
    send_message_thread.start()
    return
