# asdf-users/project/api/users.py


from flask import Blueprint, request
from sqlalchemy import exc, or_
from project.api.models import User
from project.api.utils import add_user, error_response, success_response, authenticate, is_admin
from project import db


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users/ping', methods=['GET'])
def ping_pong():
    """ GET /users/ping
    ping pong

    :return: Flask Response
    """

    return success_response('pong!')


@users_blueprint.route('/users', methods=['GET'])
def get_users():
    """ GET /users
    Fetches a list of users.

    :return: Flask Response
    """

    users = User.query.order_by(User.created_at.desc()).all()
    # TODO use serialize
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        })
    return success_response(
        'Users fetched.',
        data={'users': user_list}
    ), 200


@users_blueprint.route('/users', methods=['POST'])
@authenticate
def post_users(user_id):
    """ POST /users
    Adds a new user.
    model:
        username,
        email,
        password,
        active,
        admin,
        created_at

    :param user_id:
    :return: Flask Response
    """

    if not is_admin(user_id):
        return error_response(
            'You do not have permission to do that.'
        ), 401
    data = request.get_json()
    if not data:
        return error_response(), 400
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    # TODO setup validation
    try:
        if not User.query.filter(or_(User.username == username, User.email == email)).first():
            add_user(username, email, password)
            return success_response(
                f'{email} was added!'
            ), 201
        return error_response(
            'User already exists.'
        ), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return error_response(), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """ GET /users/<user_id>
    Fetches a user with the specified id.

    :param user_id:
    :return: Flask Response
    """

    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return error_response(
                'User does not exist.'
            ), 404
        return success_response(
            f'User {user_id} fetched.',
            data={
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at
            }
        ), 200
    except ValueError:
        return error_response(
            'User does not exist.'
        ), 404
