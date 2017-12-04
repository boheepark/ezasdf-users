from flask import Blueprint, request
from sqlalchemy import exc, or_
from project.api.models import User
from project.utils import add_user, error_response, success_response
from project import db, bcrypt


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/signup', methods=['POST'])
def post_signup():
    """ POST /auth/signup
    Signs up the new user.

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
                f'User {username} signed up.',
                data={ 'token': token.decode() }
            ), 201
        return error_response('User already exists.'), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return error_response(), 400


@auth_blueprint.route('/auth/signin', methods=['POST'])
def post_signin():
    """ POST /auth/signin
    Signs in the user and fetches the user's token.

    :return: A Flask Response
    """

    data = request.get_json()
    if not data:
        return error_response(), 400
    username = data.get('username')
    password = data.get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            token = user.encode_jwt(user.id)
            if token:
                return success_response(
                    f'User {username} signed in.',
                    data={ 'token': token.decode() }
                ), 200
        return error_response('User does not exist.'), 404
    except Exception as e:
        print(e)
        return error_response('Try again.'), 500


@auth_blueprint.route('/auth/signout', methods=['GET'])
def get_signout():
    """ GET /auth/signout
    Signs out the user.

    :return: A Flask Response
    """

    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header[7:]
        id = User.decode_jwt(token)
        if isinstance(id, int):
            user = User.query.filter_by(id=id).first()
            if not user or not user.active:
                return error_response('Something went wrong. Please contact us.'), 401
            return success_response(f'User {user.username} signed out.'), 200
        elif isinstance(id, str):
            return error_response(id), 401
    return error_response('Provide a valid token.'), 403


@auth_blueprint.route('/auth/profile', methods=['GET'])
def get_status():
    """ GET /auth/profile
    Fetches the user's profile data.

    :return: A Flask Response
    """

    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header[7:]
        id = User.decode_jwt(token)
        if not isinstance(id, str):
            user = User.query.filter_by(id=id).first()
            return success_response(
                f"Fetched {user.username}'s profile data.",
                data={
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'active': user.active,
                    'created_at': user.created_at
                }
            ), 200
        return error_response(id), 401
    return error_response('Provide a valid token.'), 401
