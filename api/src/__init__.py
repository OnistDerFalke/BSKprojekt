from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

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

    return app
