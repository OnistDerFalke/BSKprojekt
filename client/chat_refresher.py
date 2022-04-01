import api_gate
import chat
import datamanager

import communication
# tkinter root using to adding widgets from other scripts
ROOT = None

# information about target which chat window is currently opened
ACTIVE_USERNAME = None
ACTIVE_ID = None
ACTIVE_PORT = None


# injecting tkinter root to script
def root_injector(root):
    global ROOT
    ROOT = root


# refreshing chat -> update with new messages
def refresh_chat():
    chat.generate_chat(ROOT, ACTIVE_USERNAME, ACTIVE_ID)
    return


# refreshing users' list -> update with new users available
def refresh_users_list():
    if not communication.REGISTERED:
        return
    users = api_gate.get_users_list()
    for user in users:
        datamanager.create_user_data_storage(user["name"])
    chat.generate_user_list(ROOT)

