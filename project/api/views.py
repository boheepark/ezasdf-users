from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from project.api.models import User
from project import db

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@users_blueprint.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    users = User.query.all()
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
def add_user():
    post_data = request.get_json()
    if not post_data:
        return jsonify({
            'status': 'fail',
            'message': 'Invalid payload.'
        }), 400
    username = post_data.get('username')
    email = post_data.get('email')
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            db.session.add(User(username=username, email=email))
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': f'{email} was added!'
            }), 201
        else:
            return jsonify({
                'status': 'fail',
                'message': 'Sorry. That email already exists.'
            }), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify({
            'status': 'fail',
            'message': 'Invalid payload.'
        }), 400

@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details"""
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify({
                'status': 'fail',
                'message': 'User does not exist'
            }), 404
        else:
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