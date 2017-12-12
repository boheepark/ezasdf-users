import datetime
from flask import current_app
import jwt
from project import db, bcrypt


class User(db.Model):
    """ User model """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, email, password, created_at=datetime.datetime.utcnow()):
        """ __init__

        :param username:
        :param email:
        :param password:
        :param created_at:
        """

        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.created_at = created_at

    def encode_jwt(self, user_id):
        """ Generates the jwt token.

        :param user_id:
        :return: bytes|error
        """

        try:
            return jwt.encode(
                {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(
                        days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                        seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                    ),
                    'iat': datetime.datetime.utcnow(),
                    'sub': user_id
                },
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_jwt(token):
        """ Decodes the jwt token.

        :param token:
        :return: integer|string
        """

        try:
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Signin again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Signin again.'
