from sqlalchemy.exc import IntegrityError
from project import db
from project.api.models import User
from project.api.utils import add_user
from project.tests.base import BaseTestCase
from project.tests.utils import (
    TEST_USERNAME,
    TEST_USERNAME2,
    TEST_EMAIL,
    TEST_EMAIL2,
    TEST_PASSWORD
)


class TestUserModel(BaseTestCase):
    """ Tests for the User model. """

    def test_add_user(self):
        """ Verify a new user can be added to the database. """

        new_user = add_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.assertTrue(new_user.id)
        self.assertEqual(new_user.username, TEST_USERNAME)
        self.assertEqual(new_user.email, TEST_EMAIL)
        self.assertTrue(new_user.password)
        self.assertTrue(new_user.active)
        self.assertTrue(new_user.created_at)
        self.assertFalse(new_user.admin)

    def test_add_user_duplicate_username(self):
        """ Verify adding a user with a duplicate username raises an error. """

        add_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        duplicate_user = User(
            username=TEST_USERNAME,
            email=TEST_EMAIL2,
            password=TEST_PASSWORD
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        """ Verify adding a user with a duplicate email raises an error. """

        add_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        duplicate_user = User(
            username=TEST_USERNAME2,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_passwords_are_random(self):
        """ Verify passwords are random. """

        user1 = add_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        user2 = add_user(TEST_USERNAME2, TEST_EMAIL2, TEST_PASSWORD)
        self.assertNotEqual(user1.password, user2.password)

    def test_encode_jwt(self):
        """ Verify encode_jwt encodes an id to a token. """

        new_user = add_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        token = new_user.encode_jwt(new_user.id)
        self.assertTrue(isinstance(token, bytes))

    def test_decode_jwt(self):
        """ Verify decode_jwt_token decodes a token to an id. """

        new_user = add_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        token = new_user.encode_jwt(new_user.id)
        self.assertTrue(isinstance(token, bytes))
        self.assertEqual(User.decode_jwt(token), new_user.id)