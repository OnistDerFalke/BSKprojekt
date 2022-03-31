from tkinter import filedialog
import submit


# uploading file from local disc
def upload_file():
    submit.file = filedialog.askopenfilename()
    submit.filePath.set(submit.file)
    return
