from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint

import os


# Create global instances of api, application and database models.
# That allows other packages to get app, api and db variables used by whole application.
api = None
app = None
db = None


def create_app(test_config=None):
    # create and configure the app
    global app
    app = Flask(__name__,
                instance_path=os.path.abspath(os.path.dirname(__file__)))

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('../config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    global db
    db = SQLAlchemy(app)

    global api
    api = Api(app)

    # ---------------------------------------------------------------------
    # It is place for imports and initializations of other models/view stc.
    # ---------------------------------------------------------------------
    from api_users.src.user.controller.user_controller import UsersAPI, UsersByIdAPI
    api.add_resource(UsersAPI, "/api/users")
    api.add_resource(UsersByIdAPI, "/api/users/<int:user_id>")

    # clear the database and create tables
    db.drop_all()
    db.create_all()

    # Add swagger to url
    if app.config.get("ADD_SWAGGER", False):
        swagger_bp = get_swaggerui_blueprint(
            app.config.get('SWAGGER_URL', '/api/swagger'),
            app.config.get('API_DEFINITION_FILE_URL', '/static/swagger/swagger.json'),
            config=app.config.get("SWAGGER_CONFIG", {})
        )
        app.register_blueprint(swagger_bp)

    return app
