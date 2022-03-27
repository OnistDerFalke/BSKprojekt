from enum import Enum


class CipherMode(Enum):
    CBC = "CBC"
    ECB = "ECB"


mode = CipherMode.CBC
mode_text = None


def change_cipher_mode():
    global mode
    if mode == CipherMode.CBC:
        mode = CipherMode.ECB
    else:
        mode = CipherMode.CBC
    mode_text.set("Mode: " + mode.value)
    return

