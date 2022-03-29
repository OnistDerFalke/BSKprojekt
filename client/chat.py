import requests
import tkinter as tk
import math
from datetime import datetime


class User:
    def __init__(self, name, id, host=None, port=None):
        self.name = name
        self.id = id
        self.host = host
        self.port = port


class Message:
    def __init__(self, is_external, receive_time, content, author):
        self.is_external = is_external
        self.receive_time = receive_time
        self.content = content
        self.author = author


def show_user_chat(user):
    return


def get_all_users():
    try:
        response = requests.get("http://localhost:8080/api/users")
        users = response.json()

        # returns users list with names, id's and used ports
        return users
    except:
        print("Could not connect to local server.")


def generate_user_list(root):
    # users = get_all_users()

    # Mock Users
    users = [User("Alex", 0), User("Johny", 1), User("Anna", 2), User("Angela", 3), User("Geralt", 4)]

    height = 180
    offset_height = 25
    user_limit = 10
    user_counter = 0
    for user in users:
        if user_counter >= user_limit:
            break
        button_text = tk.StringVar()
        button = tk.Button(root,
                           textvariable=button_text,
                           font="Raleway", bg="#2b2b2b",
                           fg="white",
                           borderwidth=0,
                           highlightthickness=0,
                           activebackground='#212121')
        button.place(x=500, y=height, height=20, width=100)
        button_text.set(user.name)
        height += offset_height
        user_counter += 1
    return


def find_author(messages):
    for message in messages:
        if message.author != "Me":
            return message.author
    return "Unknown"


def generate_chat(root):
    # Mock Messages
    # Just to see how it works right now
    messages = [Message(True, datetime.now().strftime("%H:%M"), "Hi, how are you?"
                                                                " This is very long sentence to test what"
                                                                " happens if the message is to long and if it works fine."
                                                                " Is it? If not, you will have to fix it."
                                                                "\n\nHere there were two enters it also works!",
                        "Anna"),
                Message(True, datetime.now().strftime("%H:%M"), "Very nice to meet you!", "Anna"),
                Message(False, datetime.now().strftime("%H:%M"), "Hello Anna, I like apples.", "Me"),
                Message(True, datetime.now().strftime("%H:%M"), "Wow, you too? Let's go to eat some together!", "Anna"),
                Message(False, datetime.now().strftime("%H:%M"), "Of course!", "Me")]

    height = 190
    offset_height = 35
    user_limit = 10
    user_counter = 0

    chat_title = tk.Label(root, text=find_author(messages), font=("Raleway", 16, "bold"), bg="#212121", fg="white")
    chat_title.place(x=125, y=145, height=30, width=300)

    for message in messages:
        if user_counter >= user_limit:
            break

        # extension for longer messages
        lines_needed = math.floor(len(message.content) / 60)
        lines_needed += message.content.count('\n')
        additional_height = lines_needed * 10

        if message.is_external:
            x_location = 25
            x_label_location = x_location - 7
            x_time_label_location = x_location + 300
            anchor = 'w'
            label_color = "#bababa"
        else:
            x_location = 175
            x_label_location = x_location + 302
            x_time_label_location = x_location - 22
            anchor = 'e'
            label_color = "#333333"
        cloud_label = tk.Label(root, text="", bg=label_color)
        chat_cloud = tk.Text(root, font=("Raleway", 8), bg="#595959", fg="white", borderwidth=0, highlightthickness=0)
        chat_cloud.insert(tk.END, message.content)
        chat_cloud.config(state='disabled')
        time_label = tk.Label(root, text=message.receive_time, font=("Raleway", 6), bg="#212121", fg="white")
        chat_cloud.place(x=x_location, y=height, height=25 + additional_height, width=300)
        cloud_label.place(x=x_label_location, y=height, height=25 + additional_height, width=5)
        time_label.place(x=x_time_label_location, y=height + 16 + additional_height, height=10, width=20)
        height += offset_height + additional_height
        user_counter += 1
    return
