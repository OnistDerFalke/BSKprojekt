import json
from os.path import exists


# creating local json storage for conversation with username given
def create_user_data_storage(name):

    # preventing no name errors (but if it happens, it's probably a bug)
    if name is None:
        print("Could not create user data storage, name given was None "
              "\n-> Is it not a bug? \n-> It should not happen!")
        return

    filedir = "data/"
    filename = name+".json"
    if not exists(filedir+filename):
        print(f"Creating storage for conversation with {name}")
        with open(filedir+filename, 'w') as file:
            message_buffer = {
                "message_list": []
            }
            json.dump(message_buffer, file)
    return


# adding new text message to local storage
def add_text_message(name, realname, id, target_id, message, send_time, is_external, is_sent = True):
    filedir = "data/"
    filename = realname + ".json"
    message_data = {
        "type": "text_message",
        "message": message,
        "author": name,
        "send_time": send_time,
        "is_external": is_external,
        "id": id,
        "target_id": target_id,
        "is_sent": is_sent,
        "acknowledgement": False
    }
    with open(filedir+filename, 'r+') as file:
        file_data = json.load(file)
        file_data["message_list"].append(message_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)
    return message_data


# adding new upload message to local storage
def add_upload_message(name, realname, id, target_id, upload_path, send_time, file_size, is_external, is_sent=True):
    filedir = "data/"
    filename = realname + ".json"
    message_data = {
        "type": "upload_message",
        "message": upload_path,
        "author": name,
        "send_time": send_time,
        "is_external": is_external,
        "id": id,
        "target_id": target_id,
        "is_sent": is_sent,
        "file_size": file_size,
        "acknowledgement": False
    }
    with open(filedir+filename, 'r+') as file:
        file_data = json.load(file)
        file_data["message_list"].append(message_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)
    return message_data




