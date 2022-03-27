import requests


def get_all_users():
    try:
        response = requests.get("http://localhost:8080/api/users")
        users = response.json()
        return users
    except:
        print("Could not connect to local server.")
