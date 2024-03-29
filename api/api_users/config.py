# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection against *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "6wqoySaqnaR1A2VykQvi3lLOoJTH3UW2"

# Secret key for signing cookies
SECRET_KEY = "At7aew9IV8H29XQeknUfSpXA2QFpLcCY"

# Swagger configuration
ADD_SWAGGER = True
SWAGGER_URL = '/api/swagger'
API_DEFINITION_FILE_URL = '/static/swagger/swagger.json'
SWAGGER_CONFIG = {
    'app name': 'Users API Application'
}

# User authentication
USERS_KEYS_FOLDER_PATH = os.path.join(BASE_DIR, 'src', 'static', 'keys')
