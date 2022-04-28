import requests


# get list of the users from API
def get_users_list():
    try:
        response = requests.get("http://127.0.0.1:8080/api/users")
        users = response.json()
        return users
    except:
        print("Could not connect to local server.")


# registering user in API
def reg_user_in_api(username, port):
    response = requests.post('http://127.0.0.1:8080/api/users', json={
        "name": username,
        "port": port
    })
    print(f"User register with status code: {response.status_code}")


# unregistering user in API
def unreg_user_in_api(username, port):
    users = get_users_list()
    for user in users:
        if user["name"] == username and user["port"] == port:
            response = requests.delete('http://127.0.0.1:8080/api/users/'+str(user["id"]))
            print(f"User successfully unregistered with status: {response.status_code}")
            return
    print("Could not unregister user with username and port given.")
