from flask import Blueprint, request
from sqlalchemy import exc, or_
from project.api.models import User
from project.utils import add_user, error_response, success_response
from project import db


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users', methods=['GET'])
def get_users():
    """ GET /users
    Fetches a list of users.

    :return: flask response
    """

    users = User.query.order_by(User.created_at.desc()).all()
    #TODO use serialize
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
        data={ 'users': user_list }
    ), 200


@users_blueprint.route('/users', methods=['POST'])
def post_users():
    """ POST /users
    Adds a new user.

    :return: flask response
    """

    data = request.get_json()
    if not data:
        return error_response(), 400
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    #TODO setup validation
    try:
        if not User.query.filter(or_(User.username == username, User.email == email)).first():
            add_user(username, email, password)
            return success_response(f'{email} was added!'), 201
        return error_response('User already exists.'), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return error_response(), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """ GET /users/<user_id>
    Fetches a user with the specified id.

    :param user_id:
    :return: flask response
    """

    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return error_response('User does not exist.'), 404
        return success_response(
            f'User {user_id} retrieved.',
            data={
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at
            }
        ), 200
    except ValueError:
        return error_response('User does not exist.'), 404
