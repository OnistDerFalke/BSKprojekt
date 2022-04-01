import tkinter as tk
from tkinter import *
from tkinter import ttk
from threading import Thread
from PIL import Image, ImageTk
import os

import api_gate
import chat
import chat_refresher
import cipher
import communication
import submit
import upload

# window settings
root = tk.Tk()
root.title = "GetPost"
root.geometry("600x600")
root.resizable(width=False, height=False)
root['bg'] = '#212121'


# registering user, unblocking widgets and destroying registration widget
def register_user():
    users = api_gate.get_users_list()

    # check if port or username is not taken
    if users is not None:
        for user in users:
            if user["name"] == username_entry.get():
                regerror_content.set("Username is already taken.")
                return
            if user["port"] == int(port_entry.get()):
                regerror_content.set("Port is already taken.")
                return
    else:
        print("Cannot register, no API connection.")
        return

    # closing register widget
    communication.USER = username_entry.get()
    communication.PORT = int(port_entry.get())
    username_entry.destroy()
    port_entry.destroy()
    register_button.destroy()
    username_label.destroy()
    regerror_label.destroy()
    port_label.destroy()
    communication.REGISTERED = True


# register error label
regerror_content = tk.StringVar()
regerror_label = tk.Label(root, textvariable=regerror_content, font=("Raleway", 10), bg="#212121", fg="red")
regerror_label.place(x=200, y=170)

# username text near the entry
username_label = tk.Label(root, text="Username: ", font=("Raleway", 10), bg="#212121", fg="white")
username_label.place(x=250, y=210, anchor='e')

# port text near the entry
port_label = tk.Label(root, text="Port: ", font=("Raleway", 10), bg="#212121", fg="white")
port_label.place(x=250, y=240, anchor='e')

# entry for username
username_entry = Entry(root)
username_entry.place(x=250, y=200, height=20, width=100)

# entry for port
port_entry = Entry(root)
port_entry.place(x=250, y=230, height=20, width=100)

# register submit button
register_button = tk.Button(root,
                        command=lambda: register_user(),
                        text="Register",
                        font="Raleway", bg="#2b2b2b",
                        fg="white",
                        borderwidth=0,
                        highlightthickness=0,
                        activebackground='#212121')
register_button.place(x=250, y=260, height=20, width=100)

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
progress_bar.place_forget()

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
cipher.mode_text = tk.StringVar()
cipher.mode_text.set("Mode: " + cipher.mode.value)
cipher_mode_info = tk.Label(root, textvariable=cipher.mode_text, font=("Raleway", 10), bg="#212121", fg="white")
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
users_icon_label.place(x=510, y=150, height=25, width=30)
users_header = tk.Label(root, text="Users", font=("Raleway", 12, "bold"), bg="#212121", fg="white")
users_header.place(x=540, y=150)

# refresh users button

refresh_button = tk.Button(root,
                        command=lambda: chat_refresher.refresh_users_list(),
                        text="Update",
                        font="Raleway", bg="#2b2b2b",
                        fg="white",
                        borderwidth=0,
                        highlightthickness=0,
                        activebackground='#212121')
refresh_button.place(x=490, y=490, height=30, width=100)


# submitting message from textbox and clearing it
def submit_and_clear():
    if not communication.REGISTERED:
        return
    message = text_message_box.get("1.0", "end-1c")
    submit.send_message(communication.USER, message, communication.ID,
                        chat.User(chat_refresher.ACTIVE_USERNAME, chat_refresher.ACTIVE_ID, chat_refresher.ACTIVE_PORT))
    text_message_box.delete("1.0", "end")


# send button
send_button = tk.Button(root,
                        image=send_icon,
                        command=lambda: submit_and_clear(),
                        font="Raleway", bg="#212121",
                        fg="white",
                        borderwidth=0,
                        highlightthickness=0,
                        activebackground='#212121')
send_button.place(x=550, y=532, height=30, width=35)

# cipher-mode button
cipher_button = tk.Button(root,
                          image=cipher_icon,
                          command=lambda: cipher.change_cipher_mode(),
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


# on app exit event
def exit_handler():
    api_gate.unreg_user_in_api(communication.USER, communication.PORT)
    os._exit(0)


# injecting tkinter root to chat refresher
chat_refresher.root_injector(root)

# generating users' list for the first time
chat.generate_user_list(root)

# running message listening thread
listening_thread = Thread(target=communication.receive_text_message)
listening_thread.start()

# turning on app exit event handling
root.protocol("WM_DELETE_WINDOW", exit_handler)

root.mainloop()
