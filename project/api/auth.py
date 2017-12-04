from flask import Blueprint, request
from sqlalchemy import exc, or_
from project.api.models import User
from project.utils import add_user, error_response, success_response
from project import db, bcrypt


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/signup', methods=['POST'])
def post_signup():
    """ POST /auth/signup
    :return: json
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
            auth_token = new_user.encode_auth_token(new_user.id)
            return success_response(
                f'{username} signed up.',
                data={ 'auth_token': auth_token.decode() }
            ), 201
        return error_response('User already exists.'), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return error_response(), 400


@auth_blueprint.route('/auth/signin', methods=['POST'])
def post_signin():
    """ POST /auth/signin
    :return: json
    """
    data = request.get_json()
    if not data:
        return error_response(), 400
    username = data.get('username')
    password = data.get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                return success_response(
                    f'{username} signed in.',
                    data={'auth_token': auth_token.decode()}
                ), 200
        return error_response('User does not exist.'), 404
    except Exception as e:
        print(e)
        return error_response('Try again.'), 500


@auth_blueprint.route('/auth/logout', methods=['GET'])
def get_logout():
    """ GET /auth/logout
    :return: json
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header[7:]
        id = User.decode_auth_token(auth_token)
        if isinstance(id, int):
            user = User.query.filter_by(id=id).first()
            if not user or not user.active:
                return error_response('Something went wrong. Please contact us.'), 401
            return success_response(f'{user.username} logged out.'), 200
        elif isinstance(id, str):
            return error_response(id), 401
    return error_response('Provide a valid auth token.'), 403


@auth_blueprint.route('/auth/status', methods=['GET'])
def get_status():
    """ GET /auth/status
    :return: json
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header[7:]
        id = User.decode_auth_token(auth_token)
        if not isinstance(id, str):
            user = User.query.filter_by(id=id).first()
            return success_response(
                f'Retrieved {user.username}\'s status',
                data={
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'active': user.active,
                    'created_at': user.created_at
                }
            ), 200
        return error_response(id), 401
    return error_response('Provide a valid auth token.'), 401
