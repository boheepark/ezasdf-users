import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    """ Create Flask App.

    :return: flask app
    """

    app = Flask(__name__)
    app.config.from_object(os.getenv("APP_SETTINGS"))
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)

    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)
    from project.api.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app