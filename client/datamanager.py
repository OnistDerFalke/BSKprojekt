import json
from os.path import exists


def create_user_data_storage(name, id):
    filedir = "data/"
    filename = str(id)+"_"+name+".json"
    if not exists(filedir+filename):
        with open(filedir+filename, 'w') as file:
            message_buffer = {
                "message_list": []
            }
            json.dump(message_buffer, file)
    return


def add_text_message(name, realname, id, target_id, message, send_time, is_external, is_sent = True):
    filedir = "data/"
    filename = str(target_id) + "_" + realname + ".json"
    message_data = {
        "type": "text_message",
        "message": message,
        "author": name,
        "send_time": send_time,
        "is_external": is_external,
        "id": id,
        "target_id": target_id,
        "is_sent": is_sent
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