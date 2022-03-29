import json
from os.path import exists


def create_user_data_storage(name, id):
    filedir = "data/"
    filename = str(id)+"_"+name+".json"
    with open(filedir+filename, 'w') as file:
        message_buffer = {
            "message_list": []
        }
        json.dump(message_buffer, file)
    with open(filedir+filename, 'r') as file:
        file_data = json.load(file)
    with open(filedir + filename, 'w') as file:
        file_data["message_list"].append(message_buffer)
        file.seek(0)
        json.dump(file_data, file, indent=4)
        print("Created storage for conversation with user: " + name+"#"+str(id))
    return


def add_text_message(name, id, message, send_time):
    filedir = "data/"
    filename = str(id) + "_" + name + ".json"
    message_data = {
        "type": "text_message",
        "message": message,
        "author": name,
        "send_time": send_time
    }
    with open(filedir+filename, 'r+') as file:
        file_data = json.load(file)
        file_data["message_list"].append(message_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)
    return message_data


# watch out! index is counted from last message
def read_text_message(name, id, index):
    filedir = "data/"
    filename = str(id) + "_" + name + ".json"
    file = open(filedir+filename)
    data = json.load(file)
    return data["message_list"][len(data["message_list"])-index-1]