# ezasdf-users/project/api/auth.py


from flask import Blueprint, request
from sqlalchemy import exc, or_

from project import db, bcrypt
from project.api.models import User
from project.api.utils import add_user, error_response, success_response, authenticate

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/signup', methods=['POST'])
def post_signup():
    """ POST /auth/signup
    Signs up the new user.
    requires: {
        username: 'username'
        email: 'email',
        password: 'password'
    }

    :return: flask response
    """

    data = request.get_json()
    if not data:
        return error_response(), 400
    # TODO validate
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    try:
        if not User.query.filter(or_(User.username == username, User.email == email)).first():
            new_user = add_user(username, email, password)
            token = new_user.encode_jwt(new_user.id)
            return success_response(
                '{email} signed up.'.format(email=email),
                data={'token': token.decode()}
            ), 201
        return error_response(
            'User already exists.'
        ), 400
    except (exc.IntegrityError, ValueError):
        db.session.rollback()
        return error_response(), 400


@auth_blueprint.route('/auth/signin', methods=['POST'])
def post_signin():
    """ POST /auth/get_jwt
    Signs in the user and fetches the user's token.
    requires:
        email,
        password

    :return: A Flask Response
    """

    data = request.get_json()
    if not data:
        return error_response(), 400
    email = data.get('email')
    password = data.get('password')
    try:
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            token = user.encode_jwt(user.id)
            if token:
                return success_response(
                    '{email} signed in.'.format(email=email),
                    data={'token': token.decode()}
                ), 200
        return error_response(
            'User does not exist.'
        ), 404
    except Exception as e:
        print(e)
        return error_response(
            'Try again.'
        ), 500


@auth_blueprint.route('/auth/signout', methods=['GET'])
@authenticate
def get_signout(user_id):
    """ GET /auth/signout
    Signs out the user.

    :param user_id:
    :return: Flask Response
    """

    user = User.query.filter_by(id=user_id).first()
    return success_response(
        '{email} signed out.'.format(email=user.email)
    ), 200


@auth_blueprint.route('/auth/profile', methods=['GET'])
@authenticate
def get_profile(user_id):
    """ GET /auth/profile
    Fetches the user's profile data.

    :param user_id:
    :return: Flask Response
    """

    user = User.query.filter_by(id=user_id).first()
    return success_response(
        "Fetched {email}'s profile data.".format(email=user.email),
        data={
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'active': user.active,
            'created_at': user.created_at
        }
    ), 200
