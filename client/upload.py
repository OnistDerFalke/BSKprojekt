from tkinter import filedialog
import submit

import communication

UPLOADED = False


# uploading file from local disc
def upload_file():
    if not communication.REGISTERED:
        return
    submit.file = filedialog.askopenfilename()
    submit.filePath.set(submit.file)
    global UPLOADED
    UPLOADED = True
    return
