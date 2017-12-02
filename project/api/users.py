from flask import Blueprint, jsonify, request
from sqlalchemy import exc, or_
from project.api.models import User
from project.utils import add_user
from project import db


users_blueprint = Blueprint('users', __name__, template_folder='./templates')


@users_blueprint.route('/users', methods=['GET'])
def get_users():
    """ GET request route for fetching a list of users.
    :return: json
    """
    users = User.query.order_by(User.created_at.desc()).all()
    #TODO use serialize
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        })
    return jsonify({
        'status': 'success',
        'data': {
            'users': users_list
        }
    }), 200


@users_blueprint.route('/users', methods=['POST'])
def post_add_user():
    """ POST request route for adding a new user.
    :return: json
    """
    data = request.get_json()
    if not data:
        return jsonify({
            'status': 'fail',
            'message': 'Invalid payload.'
        }), 400
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    #TODO setup validation
    try:
        if not User.query.filter(or_(User.username == username, User.email == email)).first():
            add_user(username, email, password)
            return jsonify({
                'status': 'success',
                'message': f'{email} was added!'
            }), 201
        else:
            return jsonify({
                'status': 'fail',
                'message': 'That user already exists.'
            }), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return jsonify({
            'status': 'fail',
            'message': 'Invalid payload.'
        }), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """ GET request for fetching user with specified id
    :param user_id:
    :return: json
    """
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        return jsonify({
            'status': 'success',
            'data': {
              'username': user.username,
              'email': user.email,
              'created_at': user.created_at
            }
        }), 200
    except ValueError:
        return jsonify({
            'status': 'fail',
            'message': 'User does not exist'
        }), 404