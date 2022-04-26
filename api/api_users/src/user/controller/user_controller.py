import json
import os

from api_users.src.modules.decorators import token_authentication_needed
from api_users.src.user.service.user_service import UserService
from api_users.src.user.models.models import User
from api_users.src.user.dto.dto import short_user, full_user

from flask import Response, request
from flask_restful import Resource, marshal_with


class UsersAPI(Resource):
    """ Users API controller.
    Responsible for getting all existing users and adding new users.
    Source url is /api/users
    """

    # @token_authentication_needed
    @marshal_with(short_user)
    def get(self):
        """ Get all existing Users """
        users = UserService.find_all()
        return users, 200

    # @token_authentication_needed
    def post(self):
        """ Adds new User """
        json_req = request.get_json()

        user_name, user_port = json_req.get('name', None), json_req.get('port', None)
        if user_name is None:
            return Response(json.dumps({"message": "Name of user is not in request body"}), 400)
        if user_port is None:
            return Response(json.dumps({"message": "Port of user is not in request body."}), 400)

        if not isinstance(user_name, str):
            return Response(json.dumps({"message": "Incorrect user name datatype."}), 400)
        if not isinstance(user_name, str):
            return Response(json.dumps({"message": "Incorrect user port datatype."}), 400)

        if not UserService.is_user_port_unique(user_port):
            return Response(json.dumps({"message": "User port is not unique"}), 400)

        user = User(name=user_name, port=user_port)
        if status := UserService.create(user):
            return {"id": user.id}, 201
        else:
            return Response(status=status)


class UsersByIdAPI(Resource):
    """ Users by id API controller.
    Responsible for getting, updating and deleting users with provided id.
    Source url is /api/users/<int:user_id>
    """

    # @token_authentication_needed
    @marshal_with(full_user)
    def get(self, user_id):
        """ Get existing User with provided id """
        user = UserService.find(user_id)
        if user:
            return user.dict
        else:
            return Response(status=404)

    # @token_authentication_needed
    def put(self, user_id: int):
        """ Update existing User with provided id """
        user = UserService.find(user_id)
        if user is None:
            return Response(status=404)

        json_req = request.get_json()
        new_name = json_req.get('name', None)
        if new_name:
            user.name = new_name

        new_port = json_req.get('port', None)
        if new_port:
            if UserService.is_user_port_unique(new_port):
                user.port = new_port
            else:
                return Response(json.dumps({"message": "User port is not unique"}), 400)

        if status := UserService.update(user):
            return Response(status=202)
        else:
            return Response(status=status)

    # @token_authentication_needed
    def delete(self, user_id: int):
        """ Delete existing User with provided id """
        user = UserService.find(user_id)
        if user:
            if status := UserService.delete(user.id):
                return Response(status=202)
            else:
                return Response(status=status)
        else:
            return Response(status=404)
