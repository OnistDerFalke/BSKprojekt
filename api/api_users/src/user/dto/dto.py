from flask_restful import fields

# For GET /api/users request to minimize network connection load
short_user = {
    'id': fields.Integer,
    'name': fields.String,
    'port': fields.Integer
}

# For GET /api/users/<int:user_id> request to return all user details
full_user = {
    'id': fields.Integer,
    'name': fields.String,
    'port': fields.Integer,
    'date_created': fields.String,
    'date_modified': fields.String
}
