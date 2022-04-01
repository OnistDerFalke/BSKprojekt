import tkinter as tk
import math
import json
from functools import partial

import api_gate
import chat_refresher
import communication
import datamanager

# lists of elements (for deleting existing widgets from screen)
chat_elements_list = []
users_elements_list = []


# user template
class User:
    def __init__(self, name, id, port=None):
        self.name = name
        self.id = id
        self.port = port


# message template
class Message:
    def __init__(self, is_external, receive_time, content, author, type="text_message", is_sent=True):
        self.is_external = is_external
        self.receive_time = receive_time
        self.content = content
        self.author = author
        self.type = type
        self.is_sent = is_sent


# generating users' list
def generate_user_list(root):

    # unregistered user cannot have active users shown
    if not communication.REGISTERED:
        return

    dispose_users_list()

    users = api_gate.get_users_list()
    for user in users:
        if user["name"] is None:
            print("---> OH NO CHAT")
        datamanager.create_user_data_storage(user["name"])

    # adding existing users from API
    users = []
    users_json = api_gate.get_users_list()
    for u in users_json:
        users.append(User(u["name"], u["id"], u["port"]))

    # creating buttons for each user
    height = 180
    offset_height = 25
    user_limit = 10
    user_counter = 0
    for user in users:
        # user cannot write to himself
        if user.name == communication.USER:
            continue
        # number of users seen is limited
        if user_counter >= user_limit:
            break
        button_text = tk.StringVar()
        button = tk.Button(root,
                           textvariable=button_text,
                           command=partial(generate_chat, root, user.name, user.id),
                           font="Raleway", bg="#2b2b2b",
                           fg="white",
                           borderwidth=0,
                           highlightthickness=0,
                           activebackground='#212121')
        users_elements_list.append(button)
        button.place(x=500, y=height, height=20, width=100)
        button_text.set(user.name)
        height += offset_height
        user_counter += 1
    return


# generating chat (messages view)
def generate_chat(root, username, id):

    # unregistered user cannot have chats
    if not communication.REGISTERED:
        return

    # user has no active chat window with target
    if username is None:
        return

    dispose_chat()

    # creating data storage for target
    datamanager.create_user_data_storage(username)

    # saving info about current target (port is loaded from API)
    chat_refresher.ACTIVE_USERNAME = username
    chat_refresher.ACTIVE_ID = id
    users = api_gate.get_users_list()
    for user in users:
        if user["name"] == username:
            chat_refresher.ACTIVE_PORT = user["port"]

    global chat_elements_list
    messages = []

    # importing conversation from json
    with open('data/'+username+'.json') as json_file:
        data = json.load(json_file)
        for msg in data["message_list"]:
            messages.append(Message(msg["is_external"], msg["send_time"], msg["message"], msg["author"],
                                    msg["type"], msg["is_sent"]))

    height = 190
    offset_height = 35
    max_height = 500

    # obtaining how many messages will be shown
    msg_counter = 1
    for message in reversed(messages):
        lines_needed = math.floor(len(message.content) / 60)
        lines_needed += message.content.count('\n')
        additional_height = lines_needed * 10
        height += offset_height + additional_height
        if height > max_height:
            break
        else:
            msg_counter += 1

    # chat title widget
    chat_title = tk.Label(root, text=chat_refresher.ACTIVE_USERNAME, font=("Raleway", 16, "bold"), bg="#212121", fg="white")
    chat_title.place(x=125, y=145, height=30, width=300)
    chat_elements_list.append(chat_title)

    # generating messages
    height = 190
    for message in reversed(messages):
        cloud_too_high = False
        if msg_counter <= 0:
            break
        elif msg_counter == 1:
            lines_needed = math.floor(len(message.content) / 60)
            lines_needed += message.content.count('\n')
            additional_height = lines_needed * 10
            if height + offset_height + additional_height > max_height:
                cloud_too_high = True
        else:
            lines_needed = math.floor(len(message.content) / 60)
            lines_needed += message.content.count('\n')
            additional_height = lines_needed * 10

        # obtaining if message is send from user or from our client
        if message.is_external:
            x_location = 25
            x_label_location = x_location - 7
            x_time_label_location = x_location + 300
            label_color = "#bababa"
        else:
            x_location = 175
            x_label_location = x_location + 302
            x_time_label_location = x_location - 22
            label_color = "#333333"

        if message.is_sent or (not message.is_sent and message.is_external):
            cloud_color = "#595959"
        else:
            cloud_color = "#ad0000"

        cloud_label = tk.Label(root, text="", bg=label_color)
        chat_cloud = tk.Text(root, font=("Raleway", 8), bg=cloud_color, fg="white", borderwidth=0, highlightthickness=0)
        chat_cloud.insert(tk.END, message.content)
        chat_cloud.config(state='disabled')
        time_label = tk.Label(root, text=message.receive_time, font=("Raleway", 6), bg="#212121", fg="white")

        # cutting long message to be shown even if it's too long
        if cloud_too_high:
            cloud_height = max_height - height
            time_y_pos = height + cloud_height - 10
            if cloud_height < 10:
                break
        else:
            cloud_height = 25 + additional_height
            time_y_pos = height + 16 + additional_height

        # setting up elements positions
        chat_cloud.place(x=x_location, y=height, height=cloud_height, width=300)
        cloud_label.place(x=x_label_location, y=height, height=cloud_height, width=5)
        time_label.place(x=x_time_label_location, y=time_y_pos, height=10, width=20)

        # adding elements to chat elements list (needed to clear chat)
        chat_elements_list.append(cloud_label)
        chat_elements_list.append(chat_cloud)
        chat_elements_list.append(time_label)

        # changing values for next iteration
        height += offset_height + additional_height
        msg_counter -= 1

        if cloud_too_high:
            break
    return


# removing chat from the screen
def dispose_chat():
    for element in chat_elements_list:
        element.destroy()


# removing users' list from the screen
def dispose_users_list():
    for element in users_elements_list:
        element.destroy()