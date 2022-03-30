import requests
import tkinter as tk
import math
import json

chat_elements_list = []


class User:
    def __init__(self, name, id, host=None, port=None):
        self.name = name
        self.id = id
        self.host = host
        self.port = port


class Message:
    def __init__(self, is_external, receive_time, content, author, type="text_message", is_sent = True):
        self.is_external = is_external
        self.receive_time = receive_time
        self.content = content
        self.author = author
        self.type = type
        self.is_sent = is_sent


def show_user_chat(user):
    return


def get_all_users():
    try:
        response = requests.get("http://localhost:8080/api/users")
        users = response.json()

        # returns users list with names, id's and used ports
        # TODO: Waiting for API
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
    global chat_elements_list
    messages = []

    # importing conversation from json
    with open('data/1_User1.json') as json_file:
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
    chat_title = tk.Label(root, text=find_author(messages), font=("Raleway", 16, "bold"), bg="#212121", fg="white")
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
            anchor = 'w'
            label_color = "#bababa"
        else:
            x_location = 175
            x_label_location = x_location + 302
            x_time_label_location = x_location - 22
            anchor = 'e'
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


def dispose_chat():
    for element in chat_elements_list:
        element.destroy()
