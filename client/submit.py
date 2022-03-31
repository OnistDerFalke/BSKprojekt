from datetime import datetime
import communication
import datamanager
from threading import Thread

import chat_refresher

# info about uploaded file
file = None
filePath = None


# sending message to the target (name -> this client username)
def send_message(name, message, id, target):

    # sending message when target was not chosen -> abort sending
    if chat_refresher.ACTIVE_USERNAME is None:
        return

    # adding message that client send to target to local message data
    text_message = message
    send_time = datetime.now().strftime("%H:%M")
    final_message = datamanager.add_text_message("Me", target.name, id, target.id, text_message, send_time, False,
                                                 communication.verify_connection("localhost", target.port))

    # refreshing chat to let new message appear
    chat_refresher.refresh_chat()

    # sending message to the target
    final_message["author"] = name
    send_message_thread = Thread(target=communication.send_text_message,
                                 args=("localhost", target.port, final_message,))
    send_message_thread.start()

    return
