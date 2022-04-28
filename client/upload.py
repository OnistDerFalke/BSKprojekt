from tkinter import filedialog
import submit

import communication

UPLOADED = False


# uploading file from local disc
def upload_file():
    global UPLOADED
    if not communication.REGISTERED:
        return
    submit.file = filedialog.askopenfilename()
    if submit.file == '':
        UPLOADED = False
        return
    submit.filePath.set(submit.file)
    UPLOADED = True
    return
