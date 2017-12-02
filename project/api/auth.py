from flask import Blueprint, jsonify, request
from sqlalchemy import exc, or_
from project.api.models import User
from project.utils import add_user
from project import db, bcrypt


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/signup', methods=['POST'])
def signup():
    """ POST /auth/signup
    :return: json
    """
    data = request.get_json()
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid payload.'
        }), 400
    # TODO validate
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    try:
        if not User.query.filter(or_(User.username == username, User.email == email)).first():
            new_user = add_user(username, email, password)
            auth_token = new_user.encode_auth_token(new_user.id)
            return jsonify({
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'That user already exists.'
            }), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Invalid payload.'
        }), 400


@auth_blueprint.route('/auth/signin', methods=['POST'])
def signin():
    """ POST /auth/signin
    :return: json
    """
    data = request.get_json()
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid payload.'
        }), 400
    username = data.get('username')
    password = data.get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                return jsonify({
                    'status': 'success',
                    'message': 'Successfully signed in.',
                    'auth_token': auth_token.decode()
                }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'User does not exist.'
            }), 404
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'error',
            'message': 'Try again.'
        }), 500


@auth_blueprint.route('/auth/logout', methods=['GET'])
def logout():
    """ GET /auth/logout
    :return: json
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
        id = User.decode_auth_token(auth_token)
        if not isinstance(id, str):
            return jsonify({
                'status': 'success',
                'message': 'Successfully logged out.'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': id
            }), 401
    else:
        return jsonify({
            'status': 'error',
            'message': 'Provide a valid auth token.'
        }), 403


@auth_blueprint.route('/auth/status', methods=['GET'])
def get_user_status():
    """ GET /auth/status
    :return: json
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
        id = User.decode_auth_token(auth_token)
        if not isinstance(id, str):
            user = User.query.filter_by(id=id).first()
            return jsonify({
                'status': 'success',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'active': user.active,
                    'created_at': user.created_at
                }
            }), 200
        return jsonify({
            'status': 'error',
            'message': id
        }), 401
    else:
        return jsonify({
            'status': 'error',
            'message': 'Provide a valid auth token.'
        }), 401