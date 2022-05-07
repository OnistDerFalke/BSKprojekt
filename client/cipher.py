from enum import Enum

import communication


class CipherMode(Enum):
    CBC = "CBC"
    ECB = "ECB"


# current chosen mode
mode = CipherMode.ECB
mode_text = None


# changing cipher mode
def change_cipher_mode():
    if not communication.REGISTERED:
        return
    global mode
    if mode == CipherMode.CBC:
        mode = CipherMode.ECB
    else:
        mode = CipherMode.CBC
    mode_text.set("Mode: " + mode.value)
    return

