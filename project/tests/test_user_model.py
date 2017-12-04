from sqlalchemy.exc import IntegrityError
from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.utils import add_user


class TestUserModel(BaseTestCase):
    """ Tests for the User model. """

    def test_add_user(self):
        """ Verify a new user can be added to the database. """

        new_user = add_user('test', 'test@test.com', 'test')
        self.assertTrue(new_user.id)
        self.assertEqual(new_user.username, 'test')
        self.assertEqual(new_user.email, 'test@test.com')
        self.assertTrue(new_user.password)
        self.assertTrue(new_user.active)
        self.assertTrue(new_user.created_at)

    def test_add_user_duplicate_username(self):
        """ Verify adding a user with a duplicate username raises an error. """

        add_user('test', 'test@test.com', 'test')
        duplicate_user = User(
            username='test',
            email='test2@test.com',
            password='test'
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        """ Verify adding a user with a duplicate email raises an error. """

        add_user('test', 'test@test.com', 'test')
        duplicate_user = User(
            username='test2',
            email='test@test.com',
            password='test'
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_passwords_are_random(self):
        """ Verify passwords are random. """

        user1 = add_user('test', 'test@test.com', 'test')
        user2 = add_user('test2', 'test2@test.com', 'test')
        self.assertNotEqual(user1.password, user2.password)

    def test_encode_jwt(self):
        """ Verify encode_jwt encodes an id to a token. """

        new_user = add_user('test', 'test@test.com', 'test')
        token = new_user.encode_jwt(new_user.id)
        self.assertTrue(isinstance(token, bytes))

    def test_decode_jwt(self):
        """ Verify decode_jwt_token decodes a token to an id. """

        new_user = add_user('test', 'test@test.com', 'test')
        token = new_user.encode_jwt(new_user.id)
        self.assertTrue(isinstance(token, bytes))
        self.assertEqual(User.decode_jwt(token), new_user.id)