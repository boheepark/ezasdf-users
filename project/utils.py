import datetime
from flask import jsonify
from project import db
from project.api.models import User


def success_response(message, data=None):
    """ Helper function for generating a flask success response with jsonify.

    :param message:
    :param data:
    :return: flask response
    """

    return jsonify({
        'status': 'success',
        'message': message,
        'data': data
    })


def error_response(message='Invalid payload.'):
    """ Helper function for generating a flask error response with jsonify.

    :param message:
    :return: flask response
    """

    return jsonify({
        'status': 'error',
        'message': message
    })


def add_user(username, email, password, created_at=datetime.datetime.utcnow()):
    """ Helper function for adding a new user to the database.

    :param username:
    :param email:
    :param password:
    :param created_at:
    :return: User object
    """

    new_user = User(
        username=username,
        email=email,
        password=password,
        created_at=created_at
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user