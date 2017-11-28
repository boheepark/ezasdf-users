import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.getenv("APP_SETTINGS"))
    db.init_app(app)

    from project.api.views import users_blueprint
    app.register_blueprint(users_blueprint)

    return app