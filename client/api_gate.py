import requests
import os

from token_requests import UserTokenizedRequester


# get list of the users from API
def get_users_list():
    token_path = os.path.join('token', 'token.json')
    utr = UserTokenizedRequester(token_path, 'http://127.0.0.1:8080/')
    return utr.get_users_list()


# registering user in API
def reg_user_in_api(username, port):
    token_path = os.path.join('token', 'token.json')
    utr = UserTokenizedRequester(token_path, 'http://127.0.0.1:8080/')
    utr.reg_user(username, port)


# unregistering user in API
def unreg_user_in_api(username, port):
    token_path = os.path.join('token', 'token.json')
    utr = UserTokenizedRequester(token_path, 'http://127.0.0.1:8080/')
    utr.unreg_user(username, port)
