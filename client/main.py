import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

import chat
import submit
import upload

# window settings
root = tk.Tk()
root.title = "GetPost"
root.geometry("600x600")
root.resizable(width=False, height=False)
root['bg'] = '#212121'

# logo
logo = Image.open('images/logo.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo, borderwidth=0, highlightthickness=0)
logo_label.place(x=250, y=20)

# progress bar
pb_style = ttk.Style()
pb_style.theme_use('clam')
pb_style.configure("red.Horizontal.TProgressbar", foreground='#212121', background='#212121', throughcolor='#212121')
progress_bar = ttk.Progressbar(root, orient='horizontal', mode='indeterminate', length=450,
                               style='red.Horizontal.TProgressbar')
progress_bar.place(x=25, y=576, height=10)

# users list (just a mock for now)
testbuttontext = tk.StringVar()
testbutton = tk.Button(root,
                       command=lambda: submit.send_message(text_message_box.get("1.0", "end-1c")),
                       textvariable=testbuttontext,
                       font="Raleway", bg="#212121",
                       fg="white",
                       borderwidth=0,
                       highlightthickness=0,
                       activebackground='#212121')
testbutton.place(x=500, y=180, height=20, width=80)
testbuttontext.set("mock_user")

# send icon
send_icon = Image.open('images/send_icon.png')
send_icon = ImageTk.PhotoImage(send_icon)

# upload icon
upload_icon = Image.open('images/upload_icon.png')
upload_icon = ImageTk.PhotoImage(upload_icon)

# cipher icon
cipher_icon = Image.open('images/cipher_icon.png')
cipher_icon = ImageTk.PhotoImage(cipher_icon)

# users icon
users_icon = Image.open('images/users_icon.png')
users_icon = ImageTk.PhotoImage(users_icon)

# cipher-mode info
cipher_mode_info = tk.Label(root, text="Mode: Default", font=("Raleway", 10), bg="#212121", fg="white")
cipher_mode_info.place(x=480, y=570)

# upload-file info
submit.filePath = tk.StringVar()
submit.filePath.set("")
upload_file_info = tk.Label(root, textvariable=submit.filePath, font=("Raleway", 8), bg="#212121", fg="white")
upload_file_info.place(x=25, y=510)

# textbox
text_message_box = Text(bg="#212121", borderwidth=2, relief='groove')
text_message_box.place(x=25, y=530, height=35, width=450)
text_message_box.configure(font=("Raleway", 10), fg='white', insertbackground='white')

# users tab
users_icon_label = tk.Label(image=users_icon, borderwidth=0, highlightthickness=0)
users_icon_label.place(x=500, y=150, height=25, width=30)
users_header = tk.Label(root, text="Users", font=("Raleway", 12, "bold"), bg="#212121", fg="white")
users_header.place(x=530, y=150)

# send button
send_button = tk.Button(root,
                        image=send_icon,
                        command=lambda: submit.send_message(text_message_box.get("1.0", "end-1c")),
                        font="Raleway", bg="#212121",
                        fg="white",
                        borderwidth=0,
                        highlightthickness=0,
                        activebackground='#212121')
send_button.place(x=550, y=532, height=30, width=35)

# cipher-mode button
cipher_button = tk.Button(root,
                          image=cipher_icon,
                          command=lambda: submit.send_message(text_message_box.get("1.0", "end-1c")),
                          font="Raleway", bg="#212121",
                          fg="white",
                          borderwidth=0,
                          highlightthickness=0,
                          activebackground='#212121')
cipher_button.place(x=480, y=532, height=30, width=30)

# upload button
upload_button = tk.Button(root,
                          image=upload_icon,
                          command=lambda: upload.upload_file(),
                          font="Raleway", bg="#212121",
                          fg="white",
                          borderwidth=0,
                          highlightthickness=0,
                          activebackground='#212121')
upload_button.place(x=515, y=532, height=30, width=30)

chat.get_all_users()
root.mainloop()