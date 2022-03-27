from tkinter import *
from tkinter import filedialog
import submit


def upload_file():
    submit.file = filedialog.askopenfilename()
    submit.filePath.set(submit.file)
    return
