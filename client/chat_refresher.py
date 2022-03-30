import chat

ROOT = None


def root_injector(root):
    global ROOT
    ROOT = root


def refresh_chat():
    chat.dispose_chat()
    chat.generate_chat(ROOT)
    return
